"""
API for rTorrent
"""

import aiobtclientrpc

from ... import errors, utils
from .. import base
from . import utils as rtorrent_utils

import logging  # isort:skip
_log = logging.getLogger(__name__)


class RtorrentAPI(base.APIBase, aiobtclientrpc.RtorrentRPC):
    """
    rTorrent API
    """

    async def _get_infohashes(self):
        return await self.call('download_list')

    async def _translate_rpc_error(self, coro, infohash):
        try:
            return await coro
        except aiobtclientrpc.RPCError as e:
            translation = {}
            if infohash:
                translation.update({
                    r'^Could not find info-hash\.$': errors.NoSuchTorrentError(infohash),
                    r'^Unsupported target type found\.$': errors.InvalidTorrentError(infohash),
                })
            raise e.translate(translation)

    async def _get_torrent_fields(self, infohash, *fields):
        return await self._translate_rpc_error(
            self.multicall(
                *((field, infohash) for field in fields),
                as_dict=True,
            ),
            infohash=infohash,
        )

    async def _add_torrents(self, *, torrents, location, stopped, verify):
        request_args = {
            'stopped': bool(stopped),
            'verify': bool(verify),
            'location': str(location) if location else None
        }

        async for result in super()._add_torrents(torrents, **request_args):
            yield result

    async def _add_torrent(self, torrent, *, location, stopped, verify):
        if utils.is_magnet(torrent):
            args = ['', str(torrent)]
            infohash = utils.torrent.read(torrent).infohash
            load_method = await self.get_supported_method('load.start_verbose')

        elif utils.is_infohash(torrent):
            args = ['', f'magnet:?xt=urn:btih:{torrent}']
            infohash = str(torrent)
            load_method = await self.get_supported_method('load.start_verbose')

        else:
            if utils.is_url(torrent):
                torrent_bytes = await utils.torrent.download_bytes(torrent)
            else:
                # Assume `torrent` is local file
                torrent_bytes = utils.torrent.read_bytes(torrent)

            load_method = await self.get_supported_method(
                'load.raw_start_verbose',
                'load.raw_start',
            )

            if not verify and location:
                torrent_bytes = rtorrent_utils.add_resume_fields(
                    utils.torrent.read(torrent_bytes),
                    location,
                )
            args = ['', torrent_bytes]
            infohash = utils.torrent.read(torrent_bytes).infohash

        if location:
            args.append('d.directory.set="' + location.replace('"', r'\"') + '"')

        if infohash in await self.get_infohashes():
            yield ('already_added', infohash)
            yield errors.TorrentAlreadyAdded(infohash, torrent)

        else:
            await self.call(load_method, *args)

            # Infohash is not known if `torrent` is an URL
            # Wait for command to take effect
            await utils.Monitor(
                call=self.get_infohashes,
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_contains(infohash)

            yield ('added', infohash)

            if stopped:
                yield await self.stop(infohash)
                if verify:
                    yield await self.verify(infohash)

    async def _start_torrent(self, infohash):
        # Check current state
        state = await self._get_torrent_fields(infohash, 'd.is_open', 'd.is_active')
        if state == {'d.is_open': 1, 'd.is_active': 1}:
            yield ('already_started', infohash)
            yield errors.TorrentAlreadyStarted(infohash)

        else:
            # Start torrent
            await self._translate_rpc_error(
                self.multicall(
                    ('d.open', infohash),
                    ('d.start', infohash),
                ),
                infohash=infohash,
            )

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_fields, infohash, 'd.is_open', 'd.is_active'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_equals({'d.is_open': 1, 'd.is_active': 1})

            yield ('started', infohash)

    async def _stop_torrent(self, infohash):
        # Check current state
        state = await self._get_torrent_fields(infohash, 'd.is_open', 'd.is_active')
        if state == {'d.is_open': 0, 'd.is_active': 0}:
            yield ('already_stopped', infohash)
            yield errors.TorrentAlreadyStopped(infohash)

        else:
            # Stop torrent
            await self._translate_rpc_error(
                self.multicall(
                    ('d.stop', infohash),
                    ('d.close', infohash),
                ),
                infohash=infohash,
            )

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_fields, infohash, 'd.is_open', 'd.is_active'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_equals({'d.is_open': 0, 'd.is_active': 0})

            yield ('stopped', infohash)

    async def _start_verifying(self, infohash):
        response = await self._translate_rpc_error(
            self.call('d.check_hash', infohash),
            infohash=infohash,
        )
        _log.debug('started verifying: %r', response)

    async def _torrent_is_verifying(self, infohash):
        hashing = await self._get_torrent_field(infohash, 'd.hashing')
        _log.debug('torrent_is_verifying: %r', hashing)
        return hashing != 0

    async def _get_verifying_progress(self, infohash):
        fields = await self._get_torrent_fields(infohash, 'd.chunks_hashed', 'd.size_chunks')
        chunks_hashed, size_chunks = fields.values()
        _log.debug('chunks hashed: %r / %r', chunks_hashed, size_chunks)
        return chunks_hashed / size_chunks * 100
