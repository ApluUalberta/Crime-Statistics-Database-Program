
import utils
import a4_specific_utils
import folium
from a4_specific_utils import FolioMarker

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

_DATABASE_PATH = ""

month_strs = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def menu_bar_plot_total_crimes_per_month_for_year_range():
    connection = sqlite3.connect(_DATABASE_PATH)
    crime_type = a4_specific_utils.get_and_validate_crime_type(
        "Enter the crime type you wish to return results for: ")
    if crime_type is False:
        return

    lower_limit = utils.get_and_validate_date("Enter the lower year limit you wish to return from: ")
    if lower_limit is False:
        return

    upper_limit = utils.get_and_validate_date("Enter the upper year limit you wish to return from: ")
    if upper_limit is False:
        return

    if lower_limit <= upper_limit:
        # Execute the query
        df = pd.read_sql_query("SELECT a.Month, b.total_incidents \
        FROM ( \
                Select * \
                From crime_incidents c \
                where (c.year >= ? and c.year <= ? ) \
                Group by c.month) AS a \
        LEFT JOIN (Select *,c.Month, SUM(c.incidents_count) as total_incidents \
                From crime_incidents c \
                where (c.year >= ? and c.year <= ? ) \
                and c.Crime_type = ?\
                Group by c.month) as b  on a.Month = b.Month \
        ", connection, params=(lower_limit, upper_limit, lower_limit, upper_limit, crime_type))

        # Convert month indexes to month strings
        df['Month'] = df["Month"].apply(lambda x: month_strs[x - 1])
        df.plot.bar(x="Month", y="total_incidents", title="Per month incident count for crime type {}".format(crime_type))
        plt.subplots_adjust(0.13, 0.37, 0.94, 0.92, 0.20, 0.20)

        plot_name = a4_specific_utils.generate_filename_for_question_file("Q1", "png")

        plt.plot()
        plt.savefig(plot_name, bbox_inches="tight")
        plt.show()

    else:
        utils.print_error("Upper year limit must be greater or equal to the lower year limit.")


def menu_map_of_n_least_and_most_populous_neighborhoods():
    n = utils.input_int_and_validate_with_predicate("Display the N least/most populous neightborhoods (Enter N): ",
                                                    check_if_int_is_non_negative_and_handle)
    if n is False:
        return

    # If N is greater than half of the number of neighborhoods then we need to clamp it at num_neigh / 2.
    # This is because if we have 60 records and N is 40, then the 10 smallest/largest population circles will overlap.
    num_neigh = a4_specific_utils.get_num_neighborhoods()
    largest_needs_to_take_an_extra_neigh = False
    if (n > (num_neigh / 2)):
        n = num_neigh / 2
        if num_neigh % 2 != 0:
            largest_needs_to_take_an_extra_neigh = True

    top_n = n if not largest_needs_to_take_an_extra_neigh else n + 1

    q2_get_last_item_query = "SELECT tot_pop \
                              FROM \
                              ( \
                              SELECT p.Neighbourhood_Name as n_name, (p.CANADIAN_CITIZEN + p.NON_CANADIAN_CITIZEN + p.NO_RESPONSE) as tot_pop \
                              FROM POPULATION p \
                              ) \
                              INNER JOIN COORDINATES c ON n_name = c.Neighbourhood_Name \
                              WHERE tot_pop > 0 AND c.Latitude != 0 AND c.Longitude != 0 \
                              ORDER BY tot_pop {} \
                              LIMIT ?,1"

    q2_query_str = "SELECT n_name, tot_pop, c.Latitude, c.Longitude \
                    FROM \
                    ( \
                    SELECT p.Neighbourhood_Name as n_name, (p.CANADIAN_CITIZEN + p.NON_CANADIAN_CITIZEN + p.NO_RESPONSE) as tot_pop \
                    FROM POPULATION p \
                    ) \
                    INNER JOIN COORDINATES c ON n_name = c.Neighbourhood_Name \
                    WHERE tot_pop > 0 AND tot_pop {} ? AND c.Latitude != 0 AND c.Longitude != 0 \
                    ORDER BY tot_pop {}"

    conn = sqlite3.connect(_DATABASE_PATH)
    cur = conn.cursor()

    # Get the pop of the neighborhoods at the bottom of the queries
    # The calls to string.format should be safe since we are substituing hard coded values
    bot_n_neigh_largest_pop = cur.execute(q2_get_last_item_query.format("ASC"), (n - 1,)).fetchall()[0][0]
    top_n_neigh_smallest_pop = cur.execute(q2_get_last_item_query.format("DESC"), (top_n - 1,)).fetchall()[0][0]


    # Use a where clause to capture any ties
    bot_n_neigh = cur.execute(q2_query_str.format("<=", "ASC"), (bot_n_neigh_largest_pop,)).fetchall()
    top_n_neigh = cur.execute(q2_query_str.format(">=", "DESC"), (top_n_neigh_smallest_pop,)).fetchall()

    bot_markers = create_marker_for_q2_query_items(bot_n_neigh, "red")
    top_markers = create_marker_for_q2_query_items(top_n_neigh, "blue")

    sum = 0
    for marker in top_markers:
        sum += marker.val
    avg_val = sum / len(top_markers)

    edmonton_map = a4_specific_utils.create_new_edmonton_map()
    a4_specific_utils.add_markers_to_map(edmonton_map, bot_markers, avg_val)
    a4_specific_utils.add_markers_to_map(edmonton_map, top_markers, avg_val)
    a4_specific_utils.write_map_to_file(edmonton_map, "Q2")


def menu_map_of_top_neighborhoods_for_a_given_crime():
    #print("TODO: map_of_top_neighborhoods_for_a_given_crime")
    
    connection = sqlite3.connect(_DATABASE_PATH)
    cur = connection.cursor()
    
    lower_limit = utils.input_int_and_validate_with_predicate("Enter start year: ",check_if_int_is_year_format)
    upper_limit = utils.input_int_and_validate_with_predicate("Enter end year: ",check_if_int_is_year_format)
    crime_type = input("Enter crime type: ")
    num_neighborhood = utils.input_int_and_validate_with_predicate("Enter number of neighborhoods: ",check_if_int_is_non_negative_and_handle)
    
    cur.execute("SELECT sum(i.Incidents_Count) as counts, i.Neighbourhood_Name, c.Latitude, c.Longitude \
    FROM coordinates c  \
    LEFT JOIN crime_incidents i on c.Neighbourhood_Name = i.Neighbourhood_Name  \
    WHERE i.Year >= ? AND  \
	i.Year <= ? AND  \
	i.Crime_Type = ?  \
        GROUP BY i.Neighbourhood_Name  \
        ORDER BY counts DESC  \
        LIMIT ?  " , (str(lower_limit), str(upper_limit),crime_type,str(num_neighborhood)) )
    
    nList = cur.fetchall()
    bot_of_top = nList[num_neighborhood-1][0]
    #print(nList)
    
    
    cur.execute("SELECT sum(i.Incidents_Count) as counts, i.Neighbourhood_Name, c.Latitude, c.Longitude \
    FROM coordinates c  \
    LEFT JOIN crime_incidents i on c.Neighbourhood_Name = i.Neighbourhood_Name  \
    WHERE i.Year >= ? AND  \
	i.Year <= ? AND  \
	i.Crime_Type = ? \
        GROUP BY i.Neighbourhood_Name \
        HAVING counts >= ? \
        ORDER BY counts DESC" , (str(lower_limit), str(upper_limit),crime_type, bot_of_top) )
    
    newList = cur.fetchall()
    markers = []
    avg_val = 0

    edmonton_map = a4_specific_utils.create_new_edmonton_map()

    for n in newList:
        nPopup = "%s <br> %s" % (n[1],n[0])
        markers.append(FolioMarker([n[2], n[3]], nPopup, 'crimson', n[0]))
        avg_val += n[0]

    avg_val /= len(newList)
    a4_specific_utils.add_markers_to_map(edmonton_map, markers, avg_val)
    a4_specific_utils.write_map_to_file(edmonton_map, "Q3")
    
    
    
def menu_map_of_neighborhoods_with_highest_crime_to_population_ratio():
    connection = sqlite3.connect(_DATABASE_PATH)
    cur = connection.cursor()
    
    lower_limit = utils.get_and_validate_date("Enter the lower year limit you wish to return from: ")
    if lower_limit is False:
        return

    upper_limit = utils.get_and_validate_date("Enter the upper year limit you wish to return from: ")
    if upper_limit is False:
        return

    # write the sql query
    # read in n and check if the n is of valid input
    n = utils.input_int_and_validate_with_predicate(
        "Display the Top N neighbourhoods with the highest crime rate (crime/population), (Enter N): ",
        check_if_int_is_non_negative_and_handle)
    if n is False:
        return    
    
    edmonton_map = a4_specific_utils.create_new_edmonton_map()
    
    cur.execute("SELECT n_name, tot_pop, SUM(c.Incidents_Count), CAST(tot_pop AS FLOAT) / CAST(SUM(c.Incidents_Count) AS FLOAT) as pop_crime_rat \
    FROM \
    ( \
        SELECT p.Neighbourhood_Name as n_name, (p.CANADIAN_CITIZEN + p.NON_CANADIAN_CITIZEN + p.NO_RESPONSE) as tot_pop \
        FROM POPULATION p \
    ) \
    INNER JOIN crime_incidents c ON n_name = c.Neighbourhood_Name \
    WHERE c.Year >= ? AND \
            c.Year <= ? \
    GROUP BY n_name \
    ORDER BY pop_crime_rat DESC \
    LIMIT ?", (str(lower_limit), str(upper_limit) , n)) 
    
    list_rat = cur.fetchall()
    bot_of_top = list_rat[n-1][3]
    
    #print(list_rat)
    #print(bot_of_top)
    
    
    cur.execute("SELECT n_name, tot_pop, SUM(c.Incidents_Count), CAST(tot_pop AS FLOAT) / CAST(SUM(c.Incidents_Count) AS FLOAT) as pop_crime_rat \
    FROM \
    ( \
        SELECT p.Neighbourhood_Name as n_name, (p.CANADIAN_CITIZEN + p.NON_CANADIAN_CITIZEN + p.NO_RESPONSE) as tot_pop \
        FROM POPULATION p \
    ) \
    INNER JOIN crime_incidents c ON n_name = c.Neighbourhood_Name \
    WHERE c.Year >= ? AND \
            c.Year <= ? \
    GROUP BY n_name \
    HAVING pop_crime_rat >= ?\
    ORDER BY pop_crime_rat DESC ", (str(lower_limit), str(upper_limit) , bot_of_top)) 
    
    newRat = cur.fetchall()
    
    markers = []
    avg_val = 0

    for rat in newRat:
        cur.execute("SELECT c.Neighbourhood_Name, c.Crime_type, l.Latitude, l.Longitude \
        From crime_incidents c, coordinates l \
        where c.Neighbourhood_name = ? AND \
                l.Neighbourhood_Name = c.Neighbourhood_Name \
        GROUP BY c.Crime_type \
        ORDER BY sum(c.Incidents_count) DESC LIMIT 1", (rat[0], ))
        cType = cur.fetchall()
        nPopup = "%s <br> %s <br> %s" % (cType[0][0] , cType[0][1] , rat[3])

        markers.append(FolioMarker([cType[0][2], cType[0][3]], nPopup, 'crimson', rat[3]))
        avg_val += rat[3]

    avg_val /= len(newRat)
    a4_specific_utils.add_markers_to_map(edmonton_map, markers, avg_val)
    a4_specific_utils.write_map_to_file(edmonton_map, "Q4")
    
    
def set_db_path(db_path):
    global _DATABASE_PATH
    _DATABASE_PATH = db_path


def check_if_int_is_non_negative_and_handle(int):
    if int < 0:
        utils.print_error("Expected a non-negative integer (got {})".format(int))
        return False
    return True

def check_if_int_is_year_format(int):
    if int > 9999 or int < 1000:
        utils.print_error("Expected a valid year (got {})".format(int))
        return False
    return True


def create_marker_for_q2_query_items(query_items, colour):
    list = []

    for item in query_items:
        (n_name, tot_pop, lat, long) = item
        coords = [lat, long]
        marker_str = "{}\n{}".format(n_name, tot_pop)
        list.append(FolioMarker(coords, marker_str, colour, tot_pop))
    return list
