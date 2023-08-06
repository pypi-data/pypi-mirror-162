'''Module for writing fetched result to filesystem.'''

from .fetcher import fetch, EntryNotFoundException


def _write_to_file(query: str, content: str, data_format='fasta'):
    '''Write `content` to file with name `uid`.fasta'''
    file_name = query + '.' + data_format

    with open(file_name, 'w+', encoding='utf-8') as fp:
        fp.write(content)


def fetch_and_save(query: str, data_format='fasta', dataset='uniprotkb'):
    print(f"Searching dataset '{dataset}' on uniprot.org for {query}...")
    try:
        content = fetch(query, data_format, dataset)
        print(f"Found result for {query}. "
                f"Printing to file with format '.{data_format}'...")
        _write_to_file(query, content, data_format)
        print('Done.')
    except EntryNotFoundException:
        print(f"No protein found for ID: {query}")


def fetch_and_print(query: str, data_format='fasta', dataset='uniprotkb'):
    ''''''
    try:
        content = fetch(query, data_format, dataset)
        print(f"Found result for {query}. "
                f"Printing to file with format '.{data_format}'...")
        print(content)
    except EntryNotFoundException:
        print(f"No protein found for ID: {query}")
