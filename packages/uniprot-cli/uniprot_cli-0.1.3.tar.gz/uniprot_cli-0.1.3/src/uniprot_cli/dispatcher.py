'''Dispatcher for cli arguments.'''

import sys

from .helper import print_help, VERSION
from .writer import fetch_and_save


def cli_input(text: str):
    try:
        return input(text)
    except (KeyboardInterrupt, EOFError):
        print('\nSearch cancelled.')
        sys.exit(0)


def dispatch_and_run():
    if len(sys.argv) <= 1:
        print(f"uniprot_cli version: {VERSION}")
        uniprot_id = cli_input('Enter uniprot ID: ')
        fetch_and_save(uniprot_id)
    else:
        args = sys.argv
        if len(args) == 3 and args[1] == '--id':
            uniprot_id = args[2]
            fetch_and_save(uniprot_id)
        elif len(args) == 2 and (args[1] == '--help' or args[1] == '-h'):
            print_help()
        else:
            print_help()

