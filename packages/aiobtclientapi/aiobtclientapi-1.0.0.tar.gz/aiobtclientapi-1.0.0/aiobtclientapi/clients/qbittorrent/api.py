"""
API for qBittorrent
"""

import os

import aiobtclientrpc

from ... import errors, utils
from .. import base

import logging  # isort:skip
_log = logging.getLogger(__name__)


class QbittorrentAPI(base.APIBase, aiobtclientrpc.QbittorrentRPC):
    """
    qBittorrent API
    """

    async def _get_infohashes(self):
        torrents = await self.call('torrents/info')
        return (t['hash'] for t in torrents)

    async def _get_torrent_fields(self, infohash, *fields):
        # qBittorrent returns all torrents if it can't find `infohash`. To
        # mitigate this, we must first check if infohash exists.
        known_infohashes = await self.get_infohashes()
        if infohash not in known_infohashes:
            raise errors.NoSuchTorrentError(infohash)

        else:
            torrents = await self.call('torrents/info', hashes=[infohash])
            if len(torrents) == 1:
                torrent = torrents[0]
                # Only return wanted information
                try:
                    return {field: torrent[field] for field in fields}
                except KeyError as e:
                    field = e.args[0]
                    raise errors.ValueError(f'Unknown field: {field!r}')

            raise RuntimeError(f'Unexpected response: {torrents!r}')

    async def _add_torrents(self, *, torrents, location, stopped, verify):
        request_args = {
            'paused': 'true' if stopped else 'false',
            'skip_checking': 'false' if verify else 'true',
        }
        if location:
            request_args['savepath'] = str(location)

        async for result in super()._add_torrents(torrents, **request_args):
            yield result

    async def _add_torrent(self, torrent, **request_args):
        if utils.is_magnet(torrent):
            request_args['urls'] = [str(torrent)]
            request_files = ()
            infohash = utils.torrent.read(torrent).infohash

        elif utils.is_infohash(torrent):
            request_args['urls'] = [f'magnet:?xt=urn:btih:{torrent}']
            request_files = ()
            infohash = str(torrent)

        else:
            if utils.is_url(torrent):
                torrent_bytes = await utils.torrent.download_bytes(torrent)
            else:
                # Assume `torrent` is local file
                torrent_bytes = utils.torrent.read_bytes(torrent)

            request_files = (
                ('filename', (
                    os.path.basename(torrent),   # File name
                    torrent_bytes,               # File content
                    'application/x-bittorrent',  # MIME type
                )),
            )
            infohash = utils.torrent.read(torrent_bytes).infohash

        # qBittorrent doesn't report pre-existing torrents, it just "Fails."
        if infohash in await self.get_infohashes():
            yield ('already_added', infohash)
            yield errors.TorrentAlreadyAdded(infohash, name=torrent)

        else:
            response = await self.call('torrents/add', files=request_files, **request_args)
            if response == 'Fails.':
                raise errors.InvalidTorrentError(torrent)

            else:
                # Wait for command to take effect
                await utils.Monitor(
                    call=self.get_infohashes,
                    interval=self.monitor_interval,
                    timeout=self.monitor_timeout,
                ).return_value_contains(infohash)

                yield ('added', infohash)

    async def _start_torrent(self, infohash):
        # Check current state
        state = await self._get_torrent_field(infohash, 'state')
        if not state.startswith('paused'):
            yield ('already_started', infohash)
            yield errors.TorrentAlreadyStarted(infohash)
        else:
            await self.call('torrents/resume', hashes=[infohash])

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_field, infohash, 'state'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_contains('paused', negate=True)

            yield ('started', infohash)

    async def _stop_torrent(self, infohash):
        # Check current state
        state = await self._get_torrent_field(infohash, 'state')
        if state.startswith('paused'):
            yield ('already_stopped', infohash)
            yield errors.TorrentAlreadyStopped(infohash)
        else:
            await self.call('torrents/pause', hashes=[infohash])

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_field, infohash, 'state'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_contains('paused')

            yield ('stopped', infohash)

    async def _start_verifying(self, infohash):
        response = await self.call('torrents/recheck', hashes=[infohash])
        _log.debug('started verifying: %r', response)

    async def _torrent_is_verifying(self, infohash):
        state = await self._get_torrent_field(infohash, 'state')
        _log.debug('torrent state: %r', state)
        return state.startswith('checking')

    async def _get_verifying_progress(self, infohash):
        progress = await self._get_torrent_field(infohash, 'progress')
        _log.debug('verifying progress: %r', progress)
        return progress * 100
