'''Module for writing fetched result to filesystem.'''

from .fetcher import fetch, EntryNotFoundException

def _write_to_file(uid: str, content: str):
    '''Write `content` to file with name `uid`.fasta'''
    file_name = uid + '.fasta'

    with open(file_name, 'w+', encoding='utf-8') as fp:
        fp.write(content)


def fetch_and_save(uid: str, data_format='fasta', dataset='default'):
    print(f"Searching dataset={dataset} on uniprot for {uniprot_id}...")
    try:
        content = fetch(uniprot_id)
        print(f"Found result for {uniprot_id}. "
                f"Printing to file with format '.{data_format}'...")
        _write_to_file(uniprot_id, content)
        print('Done.')
    except EntryNotFoundException:
        print(f"No protein found for ID: {uniprot_id}")
