import argparse
from os import getpid

from sockchat.network.client import Client
from sockchat.network.server import Server
from sockchat.ui_provider import ConsoleUiProvider


def main():
    print(getpid())

    parser = argparse.ArgumentParser(description='Socket chat.')
    parser.add_argument('username', type=str, nargs='?',
                        help='username for server login, only for clients')
    parser.add_argument('address', type=str, nargs='?',
                        help='address, only for clients')
    parser.add_argument('--server', dest='is_server', action='store_true',
                        help='start server (default: start client)')

    args = parser.parse_args()

    if not args.is_server:
        if args.username is None:
            raise Exception("Username is required when starting client")
        if args.username is None:
            raise Exception("Server address are required when starting client")
        Client(args.username, args.address, ConsoleUiProvider()).run()
    else:
        Server().run()


if __name__ == '__main__':
    main()
