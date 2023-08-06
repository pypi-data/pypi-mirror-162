'''Functionality for fetching individual proteins in various formats.'''

import requests

UNIPROT_URL = 'http://uniprot.org/uniprot/'


class EntryNotFoundException(BaseException):
    '''Exception for cases where a protein does not exist on uniprot.'''


def fetch_fasta(uid: str):
    '''Downloads the protein sequence from uniprot as a .fasta file.'''
    response = requests.get(UNIPROT_URL + uid + '.fasta')

    if response.status_code != 200:
        raise EntryNotFoundException()

    return response.content.decode()

