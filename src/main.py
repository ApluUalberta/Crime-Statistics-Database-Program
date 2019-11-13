# Entry point into the program.

import argparse
import pathlib

import menu_options
import utils
import a4_specific_utils


'''
Represents a menu option.
Stores the string to select it, a string reprenting it's description, and a function pointer to execute it.
'''
class MenuItem:
    def __init__(self, selection_string, description, run_func):
        self.selection_string = selection_string
        self.description = description
        self.run_func = run_func

'''
The program state, but really this just store whether or not the main menu should terminate.
'''
class ProgramState:
    def __init__(self):
        self.should_quit = False

    def terminate(self):
        self.should_quit = True


'''
Main entry point.
'''
def main():
    if not parse_and_handle_input_args():
        return

    prog_state = ProgramState()
    menu = init_menu(prog_state)

    while (not prog_state.should_quit):
        print_menu(menu)
        handle_user_input(menu)


'''
Initializes and returns the array of valid menu options.
'''
def init_menu(prog_state):
    return [
        MenuItem("1", "Q1 (Bar plot of total crimes/month for year range)",
                 menu_options.menu_bar_plot_total_crimes_per_month_for_year_range),
        MenuItem("2", "Q2 (Generate map of N most populous neighborhoods)",
                 menu_options.menu_map_of_n_least_and_most_populous_neighborhoods),
        MenuItem("3", "Q3 (Generate map of top neighborhoods for a given crime within a set of years)",
                 menu_options.menu_map_of_top_neighborhoods_for_a_given_crime),
        MenuItem("4", "Q4 (Generate map of neighborhoods with the highest crimes to population ratio)",
                 menu_options.menu_map_of_neighborhoods_with_highest_crime_to_population_ratio),
        MenuItem("q", "Quit", lambda: prog_state.terminate())
    ]

'''
Prints each defined menu item in a nice way.
'''
def print_menu(menu):
    print("--------------------")

    for menu_item in menu:
        print("{} --> {}".format(menu_item.selection_string, menu_item.description))

    print("--------------------")

'''
Checks if the user input matched any of the menu item selection strings and calls it's execute function if so.
'''
def handle_user_input(menu):
    user_input = input("")

    for menu_item in menu:
        if menu_item.selection_string == user_input:
            menu_item.run_func()
            return

    print("\"{}\" is not a valid menu choice.".format(user_input))

'''
Parses and verifies vargs and uses them for any initialization
'''
def parse_and_handle_input_args():
    parser = argparse.ArgumentParser(prog="CMPUT_291 Simple Database UI")
    parser.add_argument('--db_path', help="The path to the database file to load", required=True)
    args = parser.parse_args()


    if not validate_db_path_arg(args.db_path):
        return False

    menu_options.set_db_path(args.db_path)
    a4_specific_utils.init(args.db_path)

    return True


'''
Verifies that the database path points to a file and that the file is actually an sqlite3 db file by inspecting
the file header.
'''
def validate_db_path_arg(db_path):

    if not pathlib.Path(db_path).exists():
        utils.print_error("The supplied path to the database \"{}\" does not exist!".format(db_path))
        return False

    if not utils.file_is_a_valid_database(db_path):
        utils.print_error("Database file provided \"{}\" is not an sqlite3 database file or is corrupted!"
                          .format(db_path))
        return False

    return True


main()
