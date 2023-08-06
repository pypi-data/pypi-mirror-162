import asyncio
import time

import async_timeout

from .. import errors

import logging  # isort:skip
_log = logging.getLogger(__name__)


class Monitor:
    """
    Continuously call awaitable until it returns a predefined value

    :param call: Any awaitable that doesn't take any arguments
    :param attribute: Attribute from the return value of `call` to act on,
        e.g. if `call` returns a :class:`~.response.Response` object and you
        want to monitor its ``success`` attribute
    :param interval: Seconds to sleep before calling `call` again
    :type interval: :class:`DynamicInterval` instance or :class:`int`
    :param timeout: Maximum number of seconds overall before
        :class:`~.errors.TimeoutError` is raised
    """

    def __init__(self, call, attribute=None, interval=1, timeout=None):
        self._call = call
        self._attribute = attribute
        self._interval = interval
        self._timeout = timeout

    async def return_value_equals(self, value, negate=False):
        """
        Block until ``await call() == value``

        :param negate: Invert the result of the comparison
        """
        def condition(return_value):
            _log.debug('Monitoring: %r %s %r', value, '!=' if negate else '==', return_value)
            return (value == return_value) is (not negate)
        return await self._block_until(condition)

    async def return_value_is(self, value, negate=False):
        """
        Block until ``await call() is value``

        :param negate: Invert the result of the comparison
        """
        def condition(return_value):
            _log.debug('Monitoring: %r is%s %r', value, ' not' if negate else '', return_value)
            return (value is return_value) is (not negate)
        return await self._block_until(condition)

    async def return_value_contains(self, value, negate=False):
        """
        Block until ``value in (await call())``

        :param negate: Invert the result of the comparison
        """
        def condition(return_value):
            _log.debug('Monitoring: %r %sin %r', value, 'not ' if negate else '', return_value)
            return (value in return_value) is (not negate)
        return await self._block_until(condition)

    async def return_value_validates(self, validator, negate=False):
        """
        Block until ``validator(await call())`` is truthy

        :param negate: Invert the result of the comparison
        """
        def condition(return_value):
            _log.debug('Monitoring: %s%s(%r)', 'not ' if negate else '', validator.__qualname__, return_value)
            return bool(validator(return_value)) is (not negate)
        return await self._block_until(condition)

    async def _block_until(self, condition):
        try:
            async with async_timeout.timeout(self._timeout):
                while True:
                    return_value = await self._call()
                    if self._attribute:
                        return_value = getattr(return_value, self._attribute)
                    if condition(return_value):
                        return return_value
                    else:
                        await self._sleep()
        except asyncio.TimeoutError:
            raise errors.TimeoutError(f'Timeout after {self._timeout} seconds')

    async def _sleep(self):
        if isinstance(self._interval, (int, float)):
            await asyncio.sleep(self._interval)
        elif isinstance(self._interval, DynamicInterval):
            interval = await self._interval.next()
            await asyncio.sleep(interval)

        else:
            raise RuntimeError(f'Invalid interval: {self._interval!r}')


class DynamicInterval:
    """
    Generate intervals from `min` to `max` depending on some ongoing operation

    :param min: Minimum interval
    :param max: Maximum interval
    :param progress_getter: Callable that takes no arguments and returns a
        number from 0 to 100

        As progress approaches 100, the interval returned by :meth:`next` gets
        closer to `min`.
    :param name: Any object with a descriptive string representation (only used
        for debugging)
    """

    def __init__(self, min, max, progress_getter, name=None):
        self._min = min
        self._max = max
        self._progress_getter = progress_getter
        self._progress = 0
        self._samples = []
        self._name = name or id(self)

    @property
    def progress(self):
        """Most recent return value from `progress_getter`"""
        return self._progress

    async def sleep(self):
        """:func:`~.asyncio.sleep` if :meth:`next` returns positive interval"""
        interval = await self.next()
        if interval > 0:
            await asyncio.sleep(interval)

    async def next(self):
        """Return next delay"""
        await self._maintain_samples()

        seconds_left = await self._get_seconds_left()
        _log.debug('%s:     SECONDS LEFT: %r', self._name, seconds_left)

        # `threshold_max` is the `seconds_left` value where we start moving from
        # `self._max` to `self._min`.
        threshold_max = self._max * 3
        # `threshold_min` is the `seconds_left` value where interval is
        # always `self._min`.
        threshold_min = self._min * 3

        if seconds_left > threshold_max:
            interval = self._max
        else:
            # `factor` is a number between 1.0 and 0.0 that indicates how
            # close we are to `threshold_min`.
            factor = max(0, seconds_left - threshold_min) / (threshold_max - threshold_min)
            # Maintain interval between `self._max` and `self._min`
            # according to `factor`.
            interval = (self._max * factor) + (self._min * (1 - factor))

        _log.debug('%s: DYNAMIC INTERVAL: %r', self._name, interval)
        return interval

    async def _get_seconds_left(self):
        progress_diff = self._samples[-1][1] - self._samples[0][1]
        if progress_diff <= 0:
            # Not enough samples to estimate
            return -1
        else:
            seconds_diff = self._samples[-1][0] - self._samples[0][0]
            progress_per_second = progress_diff / seconds_diff
            progress_left = 100 - self._samples[-1][1]
            seconds_left = progress_left / progress_per_second
            return seconds_left

    async def _maintain_samples(self):
        self._progress = progress = await self._progress_getter()
        assert 0 <= progress <= 100, progress

        self._samples.append((time.monotonic(), progress))

        # Only keep the 3 newest samples
        del self._samples[:-3]
