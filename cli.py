import os
import argparse
import logging
from backend import War

INVALID_FILETYPE_MSG = "Error: Invalid file format. %s must be a .json file."
INVALID_PATH_MSG = "Error: Invalid file path/name. Path %s does not exist."


def validate_file(file_name):
    '''
    validate file name and path.
    '''
    if not valid_path(file_name):
        logging.warning(INVALID_PATH_MSG % file_name)
        quit()
    elif not valid_file_type(file_name):
        logging.warning(INVALID_FILETYPE_MSG % file_name)
        quit()
    return


def valid_file_type(file_name):
    # validate file type
    return file_name.endswith('.json')


def valid_path(path):
    # validate file path
    return os.path.exists(path)


def display(args):
    # file to be copied
    file1 = args.display[0]
    # file to copy upon
    file2 = args.display[1]

    # validate the file to be copied
    validate_file(file1)

    # validate the type of file 2
    if not valid_file_type(file2):
        logging.warning(INVALID_FILETYPE_MSG % file2)
        exit()

    war = War(file1, file2)
    war.universe_routes_model()
    # this strategy enforce the millennium_falcon to stay maximum 2 days in a planet with hunters
    war.strategy()
    war.get_max_path_probability()
    war.display_strategic_paths()


def probability(args):
    #millennium_falcon
    file1 = args.probability[0]
    #empire
    file2 = args.probability[1]

    # validate millennium_falcon file
    validate_file(file1)

    # validate the type of empire file 
    if not valid_file_type(file2):
        print(INVALID_FILETYPE_MSG % file2)
        exit()

    war = War(file1, file2)
    war.universe_routes_model()
    # this strategy enforce the millennium_falcon to stay maximum 2 days in a planet with hunters
    war.strategy()
    print(war.get_max_path_probability())


def main():
    # create parser object 
    parser = argparse.ArgumentParser(description=" strategic universe warrior!")

    parser.add_argument("-p", "--probability", type=str, nargs=2,
                        metavar=('file1', 'file2'), help="calculate probability.")
    parser.add_argument("-d", "--display", type=str, nargs=2,
                        metavar=('file1', 'file2'), help="display paths.")
    args = parser.parse_args()
    if args.probability is not None:
        probability(args)
    elif args.display is not None:
        display(args)


if __name__ == "__main__":
    main()
