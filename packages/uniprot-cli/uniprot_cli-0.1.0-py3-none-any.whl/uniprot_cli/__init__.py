'''
Main module for uniprot-dl.
'''

import sys
import requests

VERSION = 'v0.1.0'

UNIPROT_URL = 'http://uniprot.org/uniprot/'


class EntryNotFoundException(BaseException):
    '''Exception for cases where a protein does not exist on uniprot.'''


def print_help():
    '''Print some help information.'''
    print(f"uniprot_cli {VERSION}\n"
          "An unofficial uniprot client.\n"
          "\n"
          "USAGE:\n"
          "\t uniprot_dl [OPTIONS]\n"
          "\n"
          "OPTIONS:\n"
          "\t --id <uniprot_id> \t\t ID to search uniprot for\n")


def fetch_fasta(uid: str):
    '''Downloads the protein sequence from uniprot as a .fasta file.'''
    response = requests.get(UNIPROT_URL + uid + '.fasta')

    if response.status_code != 200:
        raise EntryNotFoundException()

    return response.content.decode()


def write_to_file(uid: str, content: str):
    '''Write `content` to file with name `uid`.fasta'''
    file_name = uid + '.fasta'

    with open(file_name, 'w+', encoding='utf-8') as fp:
        fp.write(content)


def main():
    if len(sys.argv) <= 1:
        print(f"uniprot_cli version: {VERSION}")
        uniprot_id = input('Enter uniprot ID: ')
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
