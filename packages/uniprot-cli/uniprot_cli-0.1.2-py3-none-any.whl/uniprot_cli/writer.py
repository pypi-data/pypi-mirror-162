''''''

def write_to_file(uid: str, content: str):
    '''Write `content` to file with name `uid`.fasta'''
    file_name = uid + '.fasta'

    with open(file_name, 'w+', encoding='utf-8') as fp:
        fp.write(content)
