import os

import torf

from ... import errors

import logging  # isort:skip
_log = logging.getLogger(__name__)


def add_resume_fields(torrent, location):
    """
    Add ``libtorremt_resume`` to `torrent`

    :param torrent: :class:`.torf.Torrent` instance
    :param location: Download path of the files in `torrent`
    """
    files = []
    with torf.TorrentFileStream(torrent, content_path=location) as filestream:
        for file in torrent.files:
            resume_fields = {
                # Number of chunks in this file
                'completed': len(filestream.get_piece_indexes_of_file(file)),
                # rtorrent_fast_resume.pl sets priority to 0 while autotorrent
                # sets it to 1. Not sure what's better or if this matters at
                # all.
                'priority': 0,
            }

            filepath = os.path.join(location, file)
            try:
                resume_fields['mtime'] = int(os.stat(filepath).st_mtime)
            except FileNotFoundError:
                _log.debug('Ignoring nonexisting file: %r', filepath)
                pass
            except OSError as e:
                msg = e.strerror if e.strerror else str(e)
                raise errors.ReadError(f'{msg}: {filepath}')

            files.append(resume_fields)

    piece_count = torrent.pieces
    torrent.metainfo['libtorrent_resume'] = {
        'files': files,
        'bitfield': piece_count,
    }
    _log.debug('Added libtorrent_resume: %r', torrent.metainfo['libtorrent_resume'])
    return torrent.dump()
