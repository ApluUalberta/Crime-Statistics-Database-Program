import sqlite3
import folium

import utils


_GENERATED_FILES_DIR = "generated_files"
_QUESTION_FILE_COUNTERS_LTABLE = {}

_FOLIUM_EDMONTON_MAP_COORDS = [53.52199, -113.49099]
_FOLIUM_AVG_RAD_SIZE = 1000
_FOLIUM_ADDITIONAL_RAD_SIZE = 75

_VALID_CRIME_TYPES = {}
_NUM_NEIGHBORHOODS = -1


class FolioMarker:
    def __init__(self, coords, str, colour, val):
        self.coords = coords
        self.str = str
        self.colour = colour
        self.val = val


def init(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    _get_crime_types_from_db(cur)
    _get_num_neighborhoods_with_some_pop_from_db(cur)


def generate_filename_for_question_file(q_num, extention):
    """ Generate a filename for one of the questions

    The filename generated is the following format: {Question-Number}-{count}.{extention} (See lab specs)
    This function should keep track of how nany files have beein generated for that question and maintain a counter.
    """

    if q_num not in _QUESTION_FILE_COUNTERS_LTABLE:
        _QUESTION_FILE_COUNTERS_LTABLE[q_num] = 1

    file_num = _QUESTION_FILE_COUNTERS_LTABLE[q_num]
    _QUESTION_FILE_COUNTERS_LTABLE[q_num] += 1
    file_name = "{}-{}.{}".format(q_num, file_num, extention)
    return "{}/{}".format(_GENERATED_FILES_DIR, file_name)


def get_and_validate_crime_type(input_prompt):
    """ Prompt the user with input_prompt, get a crime, and then validate that's it's a valid crime.

    If anything goes wrong (they enter bad input), return false. Else return the date.
    """
    # Consider doing a query on program start to populate a list of valid crimes to avoid always quering the db.
    crime_type = input(input_prompt).lower()
    if crime_type not in _VALID_CRIME_TYPES:
        utils.print_error("\"{}\" is not a valid crime type.".format(crime_type))
        return False

    # Note: We are returning the exact case of how the crime type is spelled in the database!
    return _VALID_CRIME_TYPES[crime_type]


def create_new_edmonton_map():
    """
    Creates a new map object centered on Edmonton
    """
    return folium.Map(location=_FOLIUM_EDMONTON_MAP_COORDS, zoom_start=12)


def add_markers_to_map(map, markers, avg_val):
    """ Plots the given markers on a map

    :param map: The map to add markers to
    :markers: A list of FolioMarkers that describe info for each maker to place on the map
    :avg_val: The avg value to use for the markers passed in. Any marker vals less/greater than the average will scaled.
    """

    for marker in markers:
        calc_radius = (marker.val / avg_val) * _FOLIUM_AVG_RAD_SIZE + _FOLIUM_ADDITIONAL_RAD_SIZE

        folium.Circle(
            location=marker.coords,
            popup=marker.str,
            radius=calc_radius,
            color=marker.colour,
            fill=True,
            fill_color=marker.colour
        ).add_to(map)


def write_map_to_file(map, q_num):
    """
    Writes the given map to file named appropiately by the question number
    """
    map_file_name = generate_filename_for_question_file(q_num, "html")
    map.save(map_file_name)

    print("Wrote \"{}\" to disk.".format(map_file_name))


def get_num_neighborhoods():
    return _NUM_NEIGHBORHOODS


def _get_crime_types_from_db(cur):
    cur.execute("SELECT DISTINCT Crime_Type \
                FROM crime_incidents")
    crime_type_tuples = cur.fetchall()

    crime_type_strs = utils.map_tuple_list_to_string_list(crime_type_tuples)
    for crime_type in crime_type_strs:
        _VALID_CRIME_TYPES[crime_type.lower()] = crime_type


def _get_num_neighborhoods_with_some_pop_from_db(cur):
    global _NUM_NEIGHBORHOODS
    cur.execute("SELECT COUNT(*) \
                FROM \
                ( \
                    SELECT (p.CANADIAN_CITIZEN + p.NON_CANADIAN_CITIZEN + p.NO_RESPONSE) as tot_pop \
                    FROM POPULATION p \
                ) \
                WHERE tot_pop > 0")
    _NUM_NEIGHBORHOODS = int(cur.fetchall()[0][0])
