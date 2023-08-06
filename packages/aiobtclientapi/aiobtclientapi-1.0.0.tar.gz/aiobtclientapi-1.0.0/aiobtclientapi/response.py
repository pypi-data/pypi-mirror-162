"""
API Response
"""

import asyncio
import inspect
import types

from . import errors

import logging  # isort:skip
_log = logging.getLogger(__name__)


class Response(types.SimpleNamespace):
    """
    Response to API call

    API methods of :class:`~.clients.APIBase` subclasses return an instance of
    this class.

    :param bool success: Whether the API call was successfull
    :param warnings: Sequence of :class:`~.errors.Warning` exceptions
    :param errors: Sequence of :class:`~.errors.Error` exceptions
    :param tasks: Sequence of :class:`~.asyncio.Task` instances

    Any other keyword arguments are made available as attributes. Custom reponse
    attributes should be documented by the relevant API methods.
    """

    def __init__(self, *, success, warnings=(), errors=(), tasks=(), **kwargs):
        super().__init__(
            success=bool(success),
            warnings=list(warnings),
            errors=list(errors),
            tasks=list(tasks),
            **kwargs,
        )

    @property
    def as_dict(self):
        """Provide attributes as dictionary"""
        return vars(self)

    @classmethod
    async def from_call(cls, call, attributes=None, types=None, exception=None):
        """
        Create :class:`~.Response` instance from asynchronous call

        :param call: Coroutine or asynchronous generator

            `call` may ``return``, ``yield`` or ``raise``:

                ``(attribute, value)``
                    ``attribute`` must be a valid attribute name and ``value``
                    is assigned/appended to that attribute.

                :class:`~.errors.Error` instance
                    Errors are appended to the ``errors`` attribute.
                    ``success`` is set to `False`.

                :class:`~.errors.Warning` instance
                    Warnings are appended to the ``warnings`` attribute.
                    ``success`` is kept as it is.

                :class:`~.asyncio.Task`
                    Background tasks initiated by `call` are appended to
                    ``tasks`` so they can be awaited if needed.

                :class:`NotImplementedError` instance
                    Indicates an unimplemented feature. The exception is wrapped
                    in :class:`~.errors.NotImplementedError` and appended to
                    ``errors``.

                :class:`BaseException` instance
                    All exceptions not documented above are re-raised.

        :param attributes: Mapping of custom attributes to default values

            If the default value is a :class:`list`, values from `call` for that
            attribute are appended to that list instead of replacing it.

        :param types: Mapping of custom attributes to classes

            If an attribute's value is not an instance of its class, it is
            instantiated as its class.

            For sequence attributes, each item is handled as described above.

            Attributes that don't have a type are taken as they are.

        :param exception: Exception class that wraps every item in ``errors`` or
            `None`
        """
        initial_attributes = {
            'success': True,
            'warnings': [],
            'errors': [],
            'tasks': [],
        }
        if attributes:
            initial_attributes.update(attributes)

        all_types = {
            'success': bool,
            'warnings': errors.Warning,
            'errors': errors.Error,
        }
        if types:
            all_types.update(types)

        assert all(key in initial_attributes for key in all_types)

        handler = _HandleResults(initial_attributes, all_types, exception)

        # Collect raised exceptions and returned/yielded values/exceptions
        if inspect.isasyncgen(call):
            try:
                async for value in call:
                    handler(value)
            except Exception as e:
                handler(e)

        elif inspect.isawaitable(call):
            try:
                value = await call
                handler(value)
            except Exception as e:
                handler(e)

        else:
            raise RuntimeError(f'Unsupported type: {type(call).__name__}: {call!r}')

        return cls(**handler.attributes)


class _HandleResults:
    def __init__(self, initial_attributes, types, exception):
        self._attrs = initial_attributes
        self._types = types
        self._exc = exception

    @property
    def attributes(self):
        return self._attrs

    @property
    def exception(self):
        return self._exc

    def __call__(self, result):
        if (
            isinstance(result, tuple)
            and len(result) == 2
            and isinstance(result[0], str)
        ):
            name, value = result
            self.handle_pair(name, value)

        elif isinstance(result, errors.Error):
            self.handle_errors(result)

        elif isinstance(result, errors.Warning):
            self.handle_warnings(result)

        elif isinstance(result, Response):
            self.handle_responses(result)

        elif isinstance(result, asyncio.Task):
            self.handle_tasks(result)

        elif isinstance(result, NotImplementedError):
            self._attrs['errors'].append(errors.NotImplementedError(result))

        elif isinstance(result, BaseException):
            raise result

        elif result is None:
            pass

        else:
            raise RuntimeError(f'Invalid result: {result!r}')

    def handle_pair(self, name, value):
        _log.debug('Handling pair: (%r, %r)', name, value)
        if name in self._attrs:
            if name == 'success':
                self.handle_success(value)
            elif name == 'errors':
                self.handle_errors(value)
            elif name == 'warnings':
                self.handle_warnings(value)
            elif name == 'tasks':
                self.handle_tasks(value)
            elif isinstance(self._attrs[name], list):
                self._attrs[name].append(self._ensure_type(name, value))
            else:
                self._attrs[name] = self._ensure_type(name, value)
        else:
            raise RuntimeError(f'Unknown attribute: {name!r}')

    def handle_success(self, success):
        _log.debug('Handling success: %r', success)
        # `success` can only be True if ALL previous calls were successful
        if self._attrs['success']:
            self._attrs['success'] = self._ensure_type('success', success)

    def handle_errors(self, exception):
        _log.debug('Handling error: %r', exception)
        self._attrs['success'] = False
        if self._exc:
            error = self._exc(self._ensure_type('errors', exception))
        else:
            error = self._ensure_type('errors', exception)
        self._attrs['errors'].append(error)

    def handle_warnings(self, exception):
        _log.debug('Handling warning: %r', exception)
        self._attrs['warnings'].append(self._ensure_type('warning', exception))

    def handle_responses(self, response):
        _log.debug('Handling response: %r', response)
        self._attrs['errors'].extend(response.errors)
        self._attrs['warnings'].extend(response.warnings)
        if not response.success:
            self._attrs['success'] = False

    def handle_tasks(self, task):
        _log.debug('Handling background task: %r', task)
        self._attrs['tasks'].append(task)

    def _ensure_type(self, name, value):
        cls = self._types.get(name)
        if cls and not isinstance(value, cls):
            return cls(value)
        else:
            return value
