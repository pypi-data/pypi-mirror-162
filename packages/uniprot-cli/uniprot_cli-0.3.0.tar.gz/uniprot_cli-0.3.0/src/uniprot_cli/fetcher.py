'''Functionality for fetching individual proteins in various formats.'''

import sys
import requests
from .datasources import KNOWN_DATASETS

UNIPROT_URL = 'http://uniprot.org/uniprot/'

BASE_API_URL = 'https://rest.uniprot.org/'


class EntryNotFoundException(BaseException):
    '''Exception for cases where a protein does not exist on uniprot.'''


class UnknownDataSetError(BaseException):
    '''Exception for when trying to query from an invalid data set.'''


def format_url(query: str, data_format='fasta', dataset='uniprotkb'):
    if dataset in KNOWN_DATASETS:
        return BASE_API_URL + dataset + '/' + query + '.' + data_format 
    else:
        raise UnknownDataSetError()


def fetch(query: str, data_format='fasta', dataset='uniprotkb'):
    '''Downloads the protein sequence from uniprot as a .fasta file.'''
    try:
        url = format_url(query, data_format, dataset)
        print(f"url: {url}")
    except UnknownDataSetError:
        print(f"Error - Data set: {dataset} is unknown to uniprot.")
        sys.exit(-1)
    response = requests.get(url)

    if response.status_code != 200:
        raise EntryNotFoundException()

    return response.content.decode()
