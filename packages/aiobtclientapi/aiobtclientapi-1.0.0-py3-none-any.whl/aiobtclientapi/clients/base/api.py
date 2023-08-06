"""
Base class for client APIs
"""

import abc
import asyncio
import collections

import aiobtclientrpc

from ... import errors, utils
from ...response import Response

import logging  # isort:skip
_log = logging.getLogger(__name__)


_BackgroundTask = collections.namedtuple('_BackgroundTask', ('task', 'detached'))


class APIBase(abc.ABC):
    """
    Base class for all BitTorrent client APIs

    Subclasses are expected to also inherit from a
    :class:`aiobtclientrpc.RPCBase` subclass.

    :meth:`call`, :meth:`connect` and :meth:`disconnect` catch most low-level
    exceptions and translate them into :class:`~.errors.ConnectionError`.

    Subclasses must catch :class:`aiobtclientrpc.RPCError` when making RPC
    calls (see :meth:`.aiobtclientrpc.RPCError.translate`) or populate
    :attr:`common_rpc_error_map`.
    """

    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except ValueError as e:
            raise errors.ValueError(e)
        self._background_tasks = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exception_class, exception, traceback):
        _log.debug('%s: Closing API', self.label)
        await self.wait_for_background_tasks()
        await self.disconnect()

    def create_background_task(self, coro, name=None, done_callback=None, detach=False):
        """
        Run coroutine in background

        :param coro: Coroutine or any other argument for :func:`asyncio.create_task`
        :param name: Identifier to help with debugging
        :param done_callback: Synchronous callable that is called with the
            return value of `coro`
        :param detach: Whether to wait this task to finish

            If this is set to a truthy value, `coro` is cancelled by
            :meth:`wait_for_background_tasks` and
            :class:`~.asyncio.CancelledError` is ignored.

            If this is set to a falsy value, :meth:`wait_for_background_tasks`
            blocks until `coro` has finished.

        :return: :class:`asyncio.Task` instance
        """
        # Store references to background tasks so they don't get garbage
        # collected.
        # https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
        # Also remember if we care about the task to finish or not.
        taskinfo = _BackgroundTask(
            task=asyncio.create_task(coro),
            detached=bool(detach),
        )
        self._background_tasks.append(taskinfo)

        if name:
            taskinfo.task.set_name(name)
        else:
            taskinfo.task.set_name(f'{coro.__qualname__} [{id(coro)}]')

        def done(task):
            self._background_tasks.remove(taskinfo)
            try:
                _log.debug('%s: Background task done: %r', self.label, task.get_name())
                # Raise exception from task
                result = task.result()
                if done_callback:
                    # task.result() also raises any exception from `coro`
                    done_callback(result)
            except asyncio.CancelledError:
                _log.debug('%s: Background task was cancelled: %r', self.label, task.get_name())

            except BaseException as e:
                # Exceptions from `coro` or `done_callback` end up nowhere, so
                # we print the traceback manually and beat it.
                import sys, traceback  # isort:skip
                tb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                _log.debug('%s: Background task or done_callback croaked: %r', self.label, task.get_name())
                _log.debug('%s: %s', self.label, tb)
                print(tb, file=sys.stderr)
                sys.exit(99)

        taskinfo.task.add_done_callback(done)
        return taskinfo.task

    async def wait_for_background_tasks(self):
        """
        Wait for all tasks created by :meth:`create_background_task`

        Detached tasks are cancelled first.

        Exceptions from tasks are raised here, except for
        :class:`asyncio.CancelledError` from a detached task.
        """
        for taskinfo in self._background_tasks:
            if taskinfo.detached:
                _log.debug('%s: Cancelling background task: %r', self.label, taskinfo.task.get_name())
                taskinfo.task.cancel()

        # Tasks are removed from self._background_tasks when they are done,
        # i.e. self._background_tasks changes size while we're iterating over
        # it. Wrapping it in a tuple should avoid any related issues.
        for taskinfo in tuple(self._background_tasks):
            _log.debug('%s: Waiting for background task: %r', self.label, taskinfo.task.get_name())
            try:
                await taskinfo.task
            except asyncio.CancelledError:
                if not taskinfo.detached:
                    raise
                else:
                    _log.debug('%s: Ignoring cancelled background task: %r', self.label, taskinfo.task.get_name())

    monitor_interval = 0.1
    """Seconds between requests when waiting for some change"""

    monitor_timeout = 3
    """Maximum number of seconds before waiting for something fails"""

    common_rpc_error_map = {}
    """
    Mapping of regular expressions to exceptions for all :meth:`call` calls

    See :meth:`aiobtclientrpc.RPCError.translate`.
    """

    async def call(self, *args, **kwargs):
        """
        Wrapper around :meth:`aiobtclientrpc.RPCBase.call` that handles exceptions

        This is a thin wrapper that translates the following exceptions into
        :class:`~.errors.ConnectionError`:

            * :class:`aiobtclientrpc.ConnectionError`
            * :class:`aiobtclientrpc.TimeoutError`
            * :class:`aiobtclientrpc.AuthenticationError`
        """
        try:
            return await super().call(*args, **kwargs)
        except aiobtclientrpc.AuthenticationError as e:
            raise errors.AuthenticationError(f'{e}: {self.url}')
        except aiobtclientrpc.TimeoutError as e:
            raise errors.TimeoutError(f'{e}: {self.url}')
        except aiobtclientrpc.ConnectionError as e:
            raise errors.ConnectionError(f'{e}: {self.url}')
        except aiobtclientrpc.RPCError as e:
            raise e.translate(self.common_rpc_error_map)

    async def connect(self, *args, **kwargs):
        """
        Wrapper around :meth:`aiobtclientrpc.RPCBase.connect` that handles
        exceptions

        See :meth:`call`.
        """
        try:
            return await super().connect(*args, **kwargs)
        except aiobtclientrpc.AuthenticationError as e:
            raise errors.AuthenticationError(f'{e}: {self.url}')
        except aiobtclientrpc.TimeoutError as e:
            raise errors.TimeoutError(f'{e}: {self.url}')
        except aiobtclientrpc.ConnectionError as e:
            raise errors.ConnectionError(f'{e}: {self.url}')

    async def disconnect(self, *args, **kwargs):
        """
        Wrapper around :meth:`aiobtclientrpc.RPCBase.disconnect` that handles
        exceptions

        See :meth:`call`.
        """
        try:
            return await super().disconnect(*args, **kwargs)
        except aiobtclientrpc.AuthenticationError as e:
            raise errors.AuthenticationError(f'{e}: {self.url}')
        except aiobtclientrpc.TimeoutError as e:
            raise errors.TimeoutError(f'{e}: {self.url}')
        except aiobtclientrpc.ConnectionError as e:
            raise errors.ConnectionError(f'{e}: {self.url}')

    @staticmethod
    def _normalize_infohash(infohash):
        return utils.Infohash(infohash)

    async def get_infohashes(self):
        """
        Return sequence of all known infohashes

        :raise ConnectionError: if the connection can't be established
        """
        return [
            self._normalize_infohash(infohash)
            for infohash in await self._get_infohashes()
        ]

    @abc.abstractmethod
    async def _get_infohashes(self):
        pass

    @abc.abstractmethod
    async def _get_torrent_fields(self, infohash, *fields):
        pass

    async def _get_torrent_field(self, infohash, field):
        """
        Convenience wrapper around :meth:`_get_torrent_fields` for getting a single
        field
        """
        infohash = self._normalize_infohash(infohash)
        fields = await self._get_torrent_fields(infohash, field)
        return fields[field]

    async def add(self, *torrents, location=None, stopped=False, verify=True):
        """
        Add torrents to client

        :param torrents: Paths or URLs to torrent files, ``magnet:`` URIs or
            infohashes
        :param str location: Download directory or `None` to use the default
        :param bool stopped: Whether the torrent is active right away
        :param bool verify: Whether any existing files from the torrent are
            hashed by the client to make sure they are not corrupt

        :return: :class:`~.Response` instance with these custom attributes:

            `added`
                Infohashes of successfully added torrents

            `already_added`
                Infohashes of torrents that were already added
        """
        return await Response.from_call(
            self._add_torrents(
                torrents=torrents,
                location=location,
                stopped=stopped,
                verify=verify,
            ),
            attributes={
                'added': [],
                'already_added': [],
            },
            types={
                'added': utils.Infohash,
                'already_added': utils.Infohash,
            },
            exception=errors.AddTorrentError,
        )

    async def _add_torrents(self, torrents, **kwargs):
        for torrent in torrents:
            try:
                async for result in self._add_torrent(torrent, **kwargs):
                    yield result
            except (errors.Warning, errors.Error) as e:
                # Report error/warning and keep iterating
                yield e

    @abc.abstractmethod
    async def _add_torrent(self, torrent, **kwargs):
        pass

    async def start(self, *infohashes):
        """
        Start torrent

        :param infohashes: Infohashes of the torrents to start

        :return: :class:`~.Response` instance with these custom attributes:

            `started`
                Infohashes of successfully started torrents

            `already_started`
                Infohashes of torrents that were already started
        """
        return await Response.from_call(
            self._start_torrents(infohashes),
            attributes={
                'started': [],
                'already_started': [],
            },
            types={
                'started': utils.Infohash,
                'already_started': utils.Infohash,
            },
            exception=errors.StartTorrentError,
        )

    async def _start_torrents(self, infohashes, **kwargs):
        for infohash in infohashes:
            infohash = self._normalize_infohash(infohash)
            try:
                async for result in self._start_torrent(infohash, **kwargs):
                    yield result
            except (errors.Warning, errors.Error) as e:
                # Report error/warning and keep iterating
                yield e

    @abc.abstractmethod
    async def _start_torrent(self, infohash, **kwargs):
        pass

    async def stop(self, *infohashes):
        """
        Stop torrent

        :param infohashes: Infohash of the torrents to stop

        :return: :class:`~.Response` instance with these custom attributes:

            `stopped`
                Infohashes of successfully stopped torrents

            `already_stopped`
                Infohashes of torrents that were already stopped
        """
        return await Response.from_call(
            self._stop_torrents(infohashes),
            attributes={
                'stopped': [],
                'already_stopped': [],
            },
            types={
                'stopped': utils.Infohash,
                'already_stopped': utils.Infohash,
            },
            exception=errors.StopTorrentError,
        )

    async def _stop_torrents(self, infohashes, **kwargs):
        for infohash in infohashes:
            infohash = self._normalize_infohash(infohash)
            try:
                async for result in self._stop_torrent(infohash, **kwargs):
                    yield result
            except (errors.Warning, errors.Error) as e:
                # Report error/warning and keep iterating
                yield e

    @abc.abstractmethod
    async def _stop_torrent(self, infohash, **kwargs):
        pass

    async def verify(self, *infohashes):
        """
        Initiate hash check of torrent files

        :param infohashes: Infohashes of the torrents to verify

        :return: :class:`~.Response` instance with these custom attributes:

            `verifying`
                Infohashes of torrents that are now being verified

            `already_verifying`
                Infohashes of torrents that are already being verified
        """
        return await Response.from_call(
            self._verify_torrents(infohashes),
            attributes={
                'verifying': [],
                'already_verifying': [],
            },
            types={
                'verifying': utils.Infohash,
                'already_verifying': utils.Infohash,
            },
            exception=errors.VerifyTorrentError,
        )

    async def _verify_torrents(self, infohashes):
        for infohash in infohashes:
            infohash = self._normalize_infohash(infohash)
            try:
                async for result in self._verify_torrent(infohash):
                    yield result
            except (errors.Warning, errors.Error) as e:
                # Report error/warning and keep iterating
                yield e

    async def _verify_torrent(self, infohash):
        is_verifying = await self._torrent_is_verifying(infohash)
        if is_verifying:
            _log.debug('Already verifying: %r', infohash)
            yield ('already_verifying', infohash)
            yield errors.TorrentAlreadyVerifying(infohash)
        else:
            _log.debug('Start verifying: %r', infohash)
            await self._start_verifying(infohash)

            # Wait for command to take effect
            try:
                await utils.Monitor(
                    call=utils.partial(self._torrent_is_verifying, infohash),
                    interval=0.1,
                    timeout=1,
                ).return_value_equals(True)

            except errors.TimeoutError:
                # Verifying may never start because all files are missing or
                # because the torrent is very small and verification was
                # finished before Monitor's first call.
                _log.debug('Verification finished immediately: %r', infohash)
            else:
                yield ('verifying', infohash)

    async def verify_wait(self, *infohashes, interval=(0.3, 3)):
        """
        Asynchronous generator that yields ``(infohash, progress)`` tuples

        `progress` is either a number from ``0.0`` to ``100.0`` or
        :class:`~.errors.Error` or :class:`~.errors.Warning`.

        Every infohash is yielded at least once.

        :param infohashes: Infohashes of the torrents
        :param interval: Delay between progress updates

            ``seconds``
                Always use the same delay.

            ``(seconds_min, seconds_max)``
                Dynamically change the delay based on how much time is left.
        """
        if isinstance(interval, (int, float)):
            interval_min = interval_max = interval
        elif isinstance(interval, tuple) and len(interval) == 2:
            interval_min, interval_max = interval
        else:
            raise TypeError(f'Invalid interval: {interval!r}')

        waiters = [
            self._verify_wait_torrent(
                self._normalize_infohash(infohash),
                interval_min,
                interval_max,
            )
            for infohash in infohashes
        ]

        async for coro in utils.merge_async_generators(*waiters):
            infohash, progress_or_exception = await coro
            yield (infohash, progress_or_exception)

    async def _verify_wait_torrent(self, infohash, interval_min, interval_max):
        assert isinstance(infohash, utils.Infohash)

        interval = utils.DynamicInterval(
            name=infohash,
            min=interval_min,
            max=interval_max,
            progress_getter=utils.partial(self._get_verifying_progress, infohash),
        )

        try:
            # Initial progress
            yield (infohash, await self._get_verifying_progress(infohash))

            progress = 0
            while await self._torrent_is_verifying(infohash):
                if interval.progress != progress:
                    yield (infohash, interval.progress)
                    progress = interval.progress

                await interval.sleep()

            # Final progress
            yield (infohash, await self._get_verifying_progress(infohash))

        except (errors.Error, errors.Warning) as e:
            yield (infohash, e)

    @abc.abstractmethod
    async def _torrent_is_verifying(self, infohash):
        """`True` if torrent is verifying or queued for verification"""

    @abc.abstractmethod
    async def _start_verifying(self, infohash):
        """Initiate hash check"""

    @abc.abstractmethod
    async def _get_verifying_progress(self, infohash):
        """
        Verifying progress in percent (0 to 100)

        After verification is done (:meth:`_torrent_is_verifying` returns
        `False`), return the download progress of the wanted files in percent.
        """
