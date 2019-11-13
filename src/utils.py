# Various util functions

import os.path

'''
Get an integer input and prints an errors if it got something else.
Returns False if parsing failed.
'''
def input_int(input_msg):
    user_input = input(input_msg)
    res = try_parse_int(user_input)

    if res is False:
        print("Cannot parse \"{}\" into an integer.".format(user_input))

    return res


def input_int_and_validate_with_predicate(input_msg, predicate):
    integer = input_int(input_msg)
    if integer is False:
        return False

    if predicate(integer) is False:
        return False

    return integer


'''
Tries to parse a string to an int.
Returns False on failure.
'''
def try_parse_int(string):
    try:
        return int(string)
    except Exception:
        return False


'''
Prints an error in a common format.
'''
def print_error(err_msg):
    print("Error: {}".format(err_msg))


# Assuming tuples contain only strings
'''
Transforms a list of tuples into a list of strings where each tuples elements are concatenated together into a string.
'''
def map_tuple_list_to_string_list(tuple_list):
    return list(map(_stringify_tuple, tuple_list))


# Reference: https://stackoverflow.com/questions/12932607/how-to-check-if-a-sqlite3-database-exists-in-python
'''
Returns whether or not the file is really a sqlite3 db file.
Assumes that the file exists.
'''
def file_is_a_valid_database(file_path):
    if os.path.getsize(file_path) < 100:
        return False

    with open(file_path, 'rb') as f:
        header = f.read(16)
        if header != b"SQLite format 3\x00":
            return False

    return True


def _stringify_tuple(tuple):
    str = ""
    num_elems = len(tuple)
    for idx, elem in enumerate(tuple):
        str += elem
        # Add a space if it's not the last element
        if (num_elems > idx + 1):
            str += " "
    return str


def get_and_validate_date(input_prompt):
    """ Prompt the user with input_prompt, get a date from them, and then validate the input.

    If anything goes wrong (they enter bad input), return false. Else return the date.
    """
    user_input = input(input_prompt)
    date = try_parse_int(user_input)
    if date is False:
        print_error("\"{}\" is not a valid date.".format(user_input))
        return False

    if date < 0:
        # TODO: Can we actually have the date less than 0?
        print_error("Date can not be less than 0.")
        return False

    return date
