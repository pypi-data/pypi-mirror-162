'''Dispatcher for cli arguments.'''

import sys

from fetcher import fetch_fasta, EntryNotFoundException
from helper import print_help, VERSION
from writer import write_to_file


def dispatch_and_run():
    if len(sys.argv) <= 1:
        print(f"uniprot_cli version: {VERSION}")
        try:
            uniprot_id = input('Enter uniprot ID: ')
        except (KeyboardInterrupt, EOFError):
            print('\nSearch cancelled.')
            sys.exit(0)

        print('Searching uniprot...')
        try:
            content = fetch_fasta(uniprot_id)
            print(f"Found result for {uniprot_id}. Printing to file...")
            write_to_file(uniprot_id, content)
            print('Done.')
        except EntryNotFoundException:
            print(f"No protein found for ID: {uniprot_id}")

    else:
        args = sys.argv
        if len(args) == 3 and args[1] == '--id':
            print('Searching uniprot...')
            uniprot_id = args[2]
            try:
                content = fetch_fasta(uniprot_id)
                print(f"Found result for {uniprot_id}. Printing to file...")
                write_to_file(uniprot_id, content)
                print('Done.')
            except EntryNotFoundException:
                print(f"No protein found for ID: {uniprot_id}")
        elif len(args) == 2 and (args[1] == '--help' or args[1] == '-h'):
            print_help()
        else:
            print_help()

