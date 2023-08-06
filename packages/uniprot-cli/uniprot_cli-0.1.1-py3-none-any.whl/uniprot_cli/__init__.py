'''
Main module for uniprot-dl.
'''
from dispatcher import dispatch_and_run


def main():
    dispatch_and_run()


if __name__ == '__main__':
    main()
