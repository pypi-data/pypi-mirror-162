'''Help information for the cli.'''

VERSION = 'v0.1.3'

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
