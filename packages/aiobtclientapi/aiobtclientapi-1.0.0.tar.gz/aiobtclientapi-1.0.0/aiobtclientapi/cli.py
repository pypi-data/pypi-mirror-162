"""
Basic CLI for manual testing purposes
"""

import argparse
import asyncio
import inspect
import sys

import aiobtclientapi


def enable_debugging(*modules):
    import logging
    logging.basicConfig(
        format='%(asctime)s.%(msecs)01d %(name)s %(message)s',
        datefmt='%H:%M:%S',
    )

    logger_names = tuple(logging.root.manager.loggerDict)
    for module in modules:
        for name in logger_names:
            if name.startswith(module):
                logging.getLogger(name).setLevel(logging.DEBUG)


def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('CLIENT_NAME')
    parser.add_argument('CLIENT_URL')
    parser.add_argument('METHOD_NAME')
    parser.add_argument('METHOD_ARGS', nargs='*')
    parser.add_argument('--debug', '-d', action='append', default=[])
    args = parser.parse_args()
    args.METHOD_ARGS = Arguments(args.METHOD_ARGS)
    return args


class Arguments:
    def __init__(self, args):
        self.posargs = []
        self.kwargs = {}
        for arg in args:
            if arg.startswith('='):
                self.posargs.append(self._convert_value(arg[1:]))
            elif '=' in arg:
                name, value = arg.split('=', maxsplit=1)
                self.kwargs[name] = self._convert_value(value)
            else:
                self.posargs.append(self._convert_value(arg))

    def _convert_value(self, value):
        value = value.rstrip(',')
        if value == 'True':
            return True
        elif value == 'False':
            return False
        elif aiobtclientapi.utils.is_infohash_regex.search(value):
            return aiobtclientapi.utils.Infohash(value)
        else:
            return value

    def __repr__(self):
        return (
            '('
            + ', '.join(str(arg) for arg in self.posargs)
            + ', '
            + ', '.join(f'{k}={v!r}' for k, v in self.kwargs.items())
            + ')'
        )


def pretty_call(method, posargs, kwargs):
    string = f'{method}('
    args = []
    if posargs:
        args.append(', '.join(f'{arg!r}' for arg in posargs))
    if kwargs:
        args.append(', '.join(f'{k}={v!r}' for k, v in kwargs.items()))
    string += ', '.join(args)
    return string + ')'


async def run_async():
    cli = parse_cli_args()

    enable_debugging(*cli.debug)

    try:
        api = aiobtclientapi.api(
            name=cli.CLIENT_NAME,
            url=cli.CLIENT_URL,
            timeout=3,
        )
    except aiobtclientapi.ValueError as e:
        print('Failed to create API:', e, file=sys.stderr)
        exit(1)

    api.set_connecting_callback(lambda: print('>>> Connection status changed:', api.status))
    api.set_connected_callback(lambda: print('>>> Connection status changed:', api.status))
    api.set_disconnected_callback(lambda: print('>>> Connection status changed:', api.status))

    async with api:
        print(f'>>> CALLING {pretty_call(cli.METHOD_NAME, cli.METHOD_ARGS.posargs, cli.METHOD_ARGS.kwargs)}')
        method = getattr(api, cli.METHOD_NAME)
        call = method(*cli.METHOD_ARGS.posargs, **cli.METHOD_ARGS.kwargs)
        if inspect.iscoroutine(call):
            response = await call
            print(f'>>> RESPONSE {pretty_call(cli.METHOD_NAME, cli.METHOD_ARGS.posargs, cli.METHOD_ARGS.kwargs)}')

            if isinstance(response, aiobtclientapi.Response):
                for field, value in response.as_dict.items():
                    print(f'>>> {field.upper():>18}: {value}')

            elif isinstance(response, list):
                for item in response:
                    print(f'>>> * {item}')

            else:
                print(f'>>> {response}')

        elif inspect.isasyncgen(call):
            try:
                async for item in call:
                    print('>>>', item)
            except aiobtclientapi.Error as e:
                print('!!!', e, file=sys.stderr)

def run_sync():
    asyncio.run(run_async())
