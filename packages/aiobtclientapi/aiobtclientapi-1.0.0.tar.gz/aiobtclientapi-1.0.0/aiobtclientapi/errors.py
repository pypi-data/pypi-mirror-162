"""
Exceptions

::

    Error
    ├── ValueError
    ├── ReadError
    ├── WriteError
    ├── NotImplementedError
    ├── ConnectionError
    │   ├── TimeoutError
    │   └── AuthenticationError
    └── ResponseError
        ├── NoSuchTorrentError
        ├── InvalidTorrentError
        ├── AddTorrentError
        ├── StartTorrentError
        ├── StopTorrentError
        └── VerifyTorrentError

    Warning
    ├── TorrentAlreadyAdded
    ├── TorrentAlreadyStarted
    ├── TorrentAlreadyStopped
    └── TorrentAlreadyVerifying
"""


class Error(Exception):
    """Parent class of all fatal exceptions"""

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and str(self) == str(other)
        )


class ValueError(Error, ValueError):
    """Invalid value"""


class ReadError(Error):
    """Failed reading operation"""


class WriteError(Error):
    """Failed writing operation"""


class NotImplementedError(Error, NotImplementedError):
    """Unimplemented or unsupported functionality"""


class ConnectionError(Error, ConnectionError):
    """Unable to connect to client"""


class TimeoutError(ConnectionError, TimeoutError):
    """Something took too long and was cancelled"""


class AuthenticationError(ConnectionError):
    """Wrong login credentials"""


class ResponseError(Error):
    """Generic error from a client API request, e.g. torrent does't exist"""

    def __new__(cls, cause, *args, **kwargs):
        self = super().__new__(cls, cause, *args, **kwargs)
        if isinstance(cause, Exception):
            self._cause = cause
        else:
            self._cause = None
        return self

    @property
    def cause(self):
        """
        :class:`Exception` that caused this error or `None`

        For example, :class:`AddTorrentError` can be caused by
        :class:`ConnectionError` or :class:`InvalidTorrentError`.
        """
        return self._cause


class NoSuchTorrentError(ResponseError):
    """Torrent identifier doesn't point to a known torrent"""

    def __init__(self, torrent):
        super().__init__(f'No such torrent: {torrent}')


class InvalidTorrentError(ResponseError):
    """Bad torrent file or magnet URI"""

    def __init__(self, torrent):
        super().__init__(f'Invalid torrent: {torrent}')


class AddTorrentError(ResponseError):
    """Failed to add torrent"""

    def __init__(self, cause):
        super().__init__(f'Adding torrent failed: {cause}')


class StartTorrentError(ResponseError):
    """Failed to start torrent"""

    def __init__(self, cause):
        super().__init__(f'Starting torrent failed: {cause}')


class StopTorrentError(ResponseError):
    """Failed to stop torrent"""

    def __init__(self, cause):
        super().__init__(f'Stopping torrent failed: {cause}')


class VerifyTorrentError(ResponseError):
    """Failed to verify torrent"""

    def __init__(self, cause):
        super().__init__(f'Verifying torrent failed: {cause}')


class Warning(Exception):
    """
    Success with acceptable, non-serious side effects (e.g. adding duplicate
    torrent)
    """

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and str(self) == str(other)
        )


class TorrentAlreadyAdded(Warning):
    """
    Torrent was already added

    :param infohash: Infohash of the torrent
    :param name: Torrent name or user-provided torrent file path, magnet URI,
        etc

    `infohash` should be a machine-readable ID while `name` should be a
    user-readable ID.
    """

    def __init__(self, infohash, name=None):
        if name and name != infohash:
            super().__init__(f'Torrent already added: {name}: {infohash}')
        else:
            super().__init__(f'Torrent already added: {infohash}')


class TorrentAlreadyStarted(Warning):
    """
    Torrent is already started

    :param infohash: Infohash of the torrent
    :param name: Torrent name or user-provided torrent file path, magnet URI,
        etc

    `infohash` should be a machine-readable ID while `name` should be a
    user-readable ID.
    """

    def __init__(self, infohash, name=None):
        if name and name != infohash:
            super().__init__(f'Torrent already started: {name}: {infohash}')
        else:
            super().__init__(f'Torrent already started: {infohash}')


class TorrentAlreadyStopped(Warning):
    """
    Torrent is already stopped

    :param infohash: Infohash of the torrent
    :param name: Torrent name or user-provided torrent file path, magnet URI,
        etc

    `infohash` should be a machine-readable ID while `name` should be a
    user-readable ID.
    """

    def __init__(self, infohash, name=None):
        if name and name != infohash:
            super().__init__(f'Torrent already stopped: {name}: {infohash}')
        else:
            super().__init__(f'Torrent already stopped: {infohash}')


class TorrentAlreadyVerifying(Warning):
    """
    Torrent is already being verified

    :param infohash: Infohash of the torrent
    :param name: Torrent name or user-provided torrent file path, magnet URI,
        etc

    `infohash` should be a machine-readable ID while `name` should be a
    user-readable ID.
    """

    def __init__(self, infohash, name=None):
        if name and name != infohash:
            super().__init__(f'Torrent already verifying: {name}: {infohash}')
        else:
            super().__init__(f'Torrent already verifying: {infohash}')
