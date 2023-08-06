'''Dispatcher for cli arguments.'''

import sys
import argparse

from .writer import fetch_and_save, fetch_and_print


VERSION = 'v0.3.0'


def cli_input(text: str, def_val=None):
    try:
        from_user = input(text)
        
        if def_val:
            return from_user if from_user != '' else def_val
        else:
            return from_user
    except (KeyboardInterrupt, EOFError):
        print('\nSearch cancelled.')
        sys.exit(0)


def get_parser():
    parser = argparse.ArgumentParser(prog='uniprot-cli', description='The Unofficial Uniprot client.')
    parser.add_argument('-q', '--query', dest='query', type=str)
    parser.add_argument('-m', '--multiple', dest='multiple', type=bool, default=False)
    parser.add_argument('-f', '--format', dest='data_format', type=str, default='fasta')
    parser.add_argument('-d', '--dataset', dest='dataset', type=str, default='uniprotkb')
    parser.add_argument('-n', '--nosave', dest='nosave', type=bool, default=False)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))

    return parser


def dispatch_and_run():
    parser = get_parser()
    args = parser.parse_args()

    if args.query is None:
        print(f"uniprot_cli version: {VERSION}")
        query = cli_input('Enter uniprot ID: ')
        data_format = cli_input(
                f"Enter data format (default: '{args.data_format}'): ", 
                args.data_format)
        dataset = cli_input(
                f"Enter data set (default: '{args.dataset}'): ",
                args.dataset
                )
        fetch_and_save(query=query, 
                data_format=data_format,
                dataset=dataset)
    else:
        if args.nosave:
            fetch_and_print(query=args.query,
                    data_format=args.data_format,
                    dataset=args.dataset)
        else:
            fetch_and_save(query=args.query,
                    data_format=args.data_format,
                    dataset=args.dataset)
