"""
Utilities
"""

import asyncio
import io
import os
import re

import httpx
import torf

from .. import constants, errors
from . import torrent
from .monitor import DynamicInterval, Monitor


# Mockable standard library tools that are used by test runners or upstream
def partial(*args, **kwargs):
    from functools import partial
    return partial(*args, **kwargs)


def is_magnet(string):
    """Return `True` if `string` is a magnet URI, `False` otherwise"""
    return str(string).lower().startswith('magnet:')


is_infohash_regex = re.compile(r'^([0-9a-fA-F]{40})$')
find_infohash_regex = re.compile(r'([0-9a-fA-F]{40})')

def is_infohash(string):
    """Return `True` if `string` looks like a torrent infohash, `False` otherwise"""
    match = is_infohash_regex.search(str(string))
    return bool(match and match.string == match.group(1))


class Infohash(str):
    """Case-insensitive string of exactly 40 hexadecimal digits"""

    # Maybe save a few bytes of RAM
    __slots__ = ()

    def __new__(cls, string):
        s = str(string)
        if not is_infohash_regex.search(s):
            raise errors.ValueError(f'Invalid infohash: {string!r}')
        else:
            return super().__new__(cls, s.lower())

    def __eq__(self, other):
        if isinstance(other, str):
            return self.lower() == other.lower()
        else:
            return NotImplemented


url_regex = re.compile(r'^(?i:[0-9a-zA-Z\+\.-]+)://')

def is_url(string):
    """Return `True` if `string` looks like an URL, `False` otherwise"""
    return bool(url_regex.search(str(string)))


def read_bytes(path, maxsize=None):
    """
    Return :class:`bytes` from file

    :param path: Path to file
    :param maxsize: Maximum size of `path` in bytes

    :raise ReadError: if reading `path` fails or size of `path` exceeds
        `maxsize` bytes
    """
    try:
        if maxsize is not None:
            size = os.path.getsize(path)
            if size > maxsize:
                raise errors.ReadError(f'Too big ({size} bytes): {path}')

        with open(path, 'rb') as f:
            return f.read()

    except OSError as e:
        msg = e.strerror if e.strerror else str(e)
        raise errors.ReadError(f'{msg}: {path}')


async def download(url, to=None, maxsize=None):
    """
    Download URL to file or return :class:`bytes`

    :param url: URL to download
    :param to: File path to store bytes from `url` in
    :param maxsize: Maximum allowed ``Content-Length`` or `None` for unlimited
        download size

    :raise ReadError: if anything goes wrong
    """
    if to:
        try:
            file = open(str(to), 'wb')
        except OSError as e:
            msg = e.strerror if e.strerror else str(e)
            raise errors.WriteError(f'{msg}: {to}')
    else:
        file = io.BytesIO()

    with file:
        try:
            await _download_to_stream(url, file, maxsize)

        except httpx.HTTPStatusError as e:
            raise errors.ReadError(f'{e.response.reason_phrase}: {url}')

        except httpx.TimeoutException:
            raise errors.ReadError(f'Timeout after {constants.HTTP_REQUEST_TIMEOUT} seconds: {url}')

        except httpx.HTTPError as e:
            raise errors.ReadError(f'{e}: {url}')

        except OSError as e:
            # Writing to `file` failed
            msg = e.strerror if e.strerror else str(e)
            if to:
                raise errors.WriteError(f'{msg}: {to}')
            else:
                raise errors.WriteError(f'{msg}')

        else:
            # Return downloaded bytes unless they were written to file
            if not to:
                file.seek(0)
                return file.read()

async def _download_to_stream(url, file, maxsize):
    client = httpx.AsyncClient(
        follow_redirects=True,
        timeout=constants.HTTP_REQUEST_TIMEOUT,
    )

    async with client:
        async with client.stream('GET', url) as response:
            # Raise exception on HTTP error, e.g. 404
            response.raise_for_status()

            if maxsize is not None:
                size = int(response.headers['Content-Length'])
                if size > maxsize:
                    raise errors.ReadError(f'Too big ({size} bytes): {url}')

            async for chunk in response.aiter_bytes():
                file.write(chunk)


async def merge_async_generators(*generators):
    """
    Combine multiple asynchronous generators into one

    Every generated value is wrapped in a coroutine that returns it or raises an
    exception raised by the generator.

    Example:

    >>> async for coro in merge_async_generators(a, b, c):
    >>>     try:
    >>>         print('Good value:', await coro)
    >>>     except ValueError as e:
    >>>         print('Bad value:', e)
    """
    aiters = [g.__aiter__() for g in generators]
    tasks = {
        asyncio.create_task(aiter.__anext__()): aiter
        for aiter in aiters
    }

    while tasks:
        done, pending_ = await asyncio.wait(
            tasks.keys(),
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in done:
            aiter = tasks[task]
            del tasks[task]
            result = exception = None
            try:
                # This also raises any exceptions from the generator
                result = task.result()
            except StopAsyncIteration:
                continue
            except Exception as e:
                exception = e
            else:
                next_task = asyncio.create_task(aiter.__anext__())
                tasks[next_task] = aiter

            async def return_result(result, exception):
                if exception:
                    raise exception
                else:
                    return result

            yield return_result(result, exception)
