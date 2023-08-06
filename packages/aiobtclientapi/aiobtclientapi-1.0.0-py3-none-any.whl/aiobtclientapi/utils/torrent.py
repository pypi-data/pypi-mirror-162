import io
import os

import torf

from .. import constants, errors, utils


def read(torrent):
    """
    Read `torrent` file or bytes into :class:`~torf.Torrent` object

    :param torrent: Path to torrent file, magnet URI or raw metainfo
        (:class:`bytes`)

    :raise ReadError: if reading `torrent` fails
    """
    try:
        if isinstance(torrent, (bytes, bytearray)):
            # Raw byte string
            return torf.Torrent.read_stream(io.BytesIO(torrent))
        elif hasattr(torrent, 'read'):
            # File-like object
            return torf.Torrent.read_stream(torrent)
        else:
            # File path
            return torf.Torrent.read(torrent)

    except torf.ReadError as e:
        if utils.is_magnet(torrent):
            # Magnet URI
            try:
                return torf.Magnet.from_string(torrent).torrent()
            except torf.MagnetError as e:
                raise errors.InvalidTorrentError(f'{e.reason}: {torrent}')
        else:
            msg = []
            if e.errno:
                msg.append(os.strerror(e.errno))
            else:
                msg.append('Failed to read')
            if e.path:
                msg.append(e.path)
            raise errors.ReadError(': '.join(msg))

    except torf.BdecodeError as e:
        if e.filepath:
            raise errors.InvalidTorrentError(e.filepath)
        else:
            raise errors.InvalidTorrentError(e)

    except torf.TorfError as e:
        # Should be torf.MetainfoError, but we catch all torf errors to be safe.
        if isinstance(torrent, str):
            raise errors.InvalidTorrentError(f'{e}: {torrent}')
        else:
            raise errors.InvalidTorrentError(e)


def read_bytes(path):
    """
    Return :class:`bytes` from torrent file

    This is just a convenient wrapper around :func:`~.read_bytes` with a
    reasonable `maxsize` argument.
    """
    return utils.read_bytes(path, maxsize=constants.MAX_TORRENT_SIZE)


async def download_bytes(url):
    """
    Return :class:`bytes` from torrent file URL

    This is just a convenient wrapper around :func:`~.download` with a
    reasonable `maxsize` argument.
    """
    return await utils.download(url, maxsize=constants.MAX_TORRENT_SIZE)
