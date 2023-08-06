"""
API for the Transmission daemon
"""

import base64
import os

import aiobtclientrpc

from ... import errors, utils
from .. import base
from . import enums

import logging  # isort:skip
_log = logging.getLogger(__name__)


class TransmissionAPI(base.APIBase, aiobtclientrpc.TransmissionRPC):
    """
    Transmission daemon API
    """

    async def _get_infohashes(self):
        response = await self.call('torrent-get', fields=['hashString'])
        return (t['hashString'] for t in response['arguments']['torrents'])

    async def _get_torrent_fields(self, infohash, *fields):
        response = await self.call('torrent-get', ids=[infohash], fields=fields)
        torrents = response['arguments']['torrents']
        if len(torrents) == 0:
            raise errors.NoSuchTorrentError(infohash)
        elif len(torrents) == 1:
            torrent = torrents[0]
            try:
                return {field: torrent[field] for field in fields}
            except KeyError as e:
                field = e.args[0]
                raise errors.ValueError(f'Unknown field: {field!r}')
        else:
            raise RuntimeError(f'Unexpected torrent list: {torrents!r}')

    async def _add_torrents(self, *, torrents, location, stopped, verify):
        # TODO: Make verification optional when/if it's ever supported upstream
        if not verify:
            yield errors.Warning(f'Adding torrents without verification is not supported by {self.label}')

        request_args = {
            'paused': bool(stopped),
        }
        if location:
            request_args['download-dir'] = str(os.path.abspath(location))

        async for result in super()._add_torrents(torrents, **request_args):
            yield result

    async def _add_torrent(self, torrent, **request_args):
        if utils.is_magnet(torrent):
            request_args['filename'] = str(torrent)

        elif utils.is_infohash(torrent):
            request_args['filename'] = f'magnet:?xt=urn:btih:{torrent}'

        else:
            if utils.is_url(torrent):
                torrent_bytes = await utils.torrent.download_bytes(torrent)
            else:
                # Assume `torrent` is local file
                torrent_bytes = utils.torrent.read_bytes(torrent)

            # Assume local file
            request_args['metainfo'] = str(
                base64.b64encode(torrent_bytes),
                encoding='ascii',
            )

        # Add torrent
        try:
            result = await self.call('torrent-add', request_args)

        except aiobtclientrpc.RPCError as e:
            raise e.translate({
                r'Invalid or corrupt': errors.InvalidTorrentError(torrent),
            })

        else:
            # Get torrent hash or error message
            arguments = result['arguments']
            if 'torrent-added' in arguments:
                infohash = arguments['torrent-added']['hashString']
                yield ('added', arguments['torrent-added']['hashString'])

            elif 'torrent-duplicate' in arguments:
                infohash = arguments['torrent-duplicate']['hashString']
                yield ('already_added', infohash)
                yield errors.TorrentAlreadyAdded(infohash, name=torrent)

            else:
                raise RuntimeError(f'Unexpected response: {result}')

    async def _start_torrent(self, infohash):
        # Check current state
        status = await self._get_torrent_field(infohash, 'status')
        if status != enums.TR_STATUS.STOPPED:
            yield ('already_started', infohash)
            yield errors.TorrentAlreadyStarted(infohash)
        else:
            await self.call('torrent-start', ids=[infohash])

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_field, infohash, 'status'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_equals(enums.TR_STATUS.STOPPED, negate=True)

            yield ('started', infohash)

    async def _stop_torrent(self, infohash):
        # Check current state
        status = await self._get_torrent_field(infohash, 'status')
        if status == enums.TR_STATUS.STOPPED:
            yield ('already_stopped', infohash)
            yield errors.TorrentAlreadyStopped(infohash)
        else:
            await self.call('torrent-stop', ids=[infohash])

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_field, infohash, 'status'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_equals(enums.TR_STATUS.STOPPED)

            yield ('stopped', infohash)

    async def _start_verifying(self, infohash):
        _log.debug('Start verifying: %r', infohash)
        await self.call('torrent-verify', ids=[infohash])

    async def _torrent_is_verifying(self, infohash):
        status = await self._get_torrent_field(infohash, 'status')
        return status in (enums.TR_STATUS.CHECK, enums.TR_STATUS.CHECK_WAIT)

    async def _get_verifying_progress(self, infohash):
        torrent = await self._get_torrent_fields(infohash, 'status', 'recheckProgress', 'percentDone')
        if torrent['status'] in (enums.TR_STATUS.CHECK, enums.TR_STATUS.CHECK_WAIT):
            return torrent['recheckProgress'] * 100
        else:
            # NOTE: Despite the name, "percentDone" is also a fraction from 0.0
            #       to 1.0.
            return torrent['percentDone'] * 100
