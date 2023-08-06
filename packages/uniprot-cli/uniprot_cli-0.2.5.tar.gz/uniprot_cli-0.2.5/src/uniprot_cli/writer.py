'''Module for writing fetched result to filesystem.'''

from .fetcher import fetch, EntryNotFoundException

def _write_to_file(uid: str, content: str):
    '''Write `content` to file with name `uid`.fasta'''
    file_name = uid + '.fasta'

    with open(file_name, 'w+', encoding='utf-8') as fp:
        fp.write(content)


def fetch_and_save(uid: str, data_format='fasta', dataset='default'):
    print(f"Searching dataset={dataset} on uniprot for {uid}...")
    try:
        content = fetch(uid)
        print(f"Found result for {uid}. "
                f"Printing to file with format '.{data_format}'...")
        _write_to_file(uid, content)
        print('Done.')
    except EntryNotFoundException:
        print(f"No protein found for ID: {uid}")
