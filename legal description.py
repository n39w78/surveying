import csv
import math
from decimal import Decimal, getcontext
import os
import textwrap
import re


def main():
    coord_list = read_csv()
    while True:
        portion_choice = input("Is this description for a portion 'P' or for an entire 'E' lot. Enter P/E: ").upper()
        if portion_choice in ['P', 'E']:
            portion = "a portion" if portion_choice == "P" else "all"
            break
        else:
            print("Invalid input. Please enter 'P' for portion or 'E' for entire lot: ")
    record, book_type, lot_number, square, book, page = get_lot_data()
    courses_list = metes_bounds(coord_list)
    last_bearing = courses_list[-1][-2]
    last_distance = courses_list[-1][-1]
    last_course_count = len(courses_list)
    area, acres = calculate_area(coord_list)
    courses = (
        '\n'.join([f"\t{i + 1}.{item[0]}, {item[1]} feet (record) to a point; thence"
                   for i, item in enumerate(courses_list[:-1])])
    )
    last_course = textwrap.fill(
        f"{last_course_count}.{last_bearing}, {last_distance} feet (record) to the point of beginning, containing "
        f"{area} square feet or {acres} acres of land",
        initial_indent='\t',
        subsequent_indent='\t',
        width=90
    )
    being_clause_text = being_clause(portion, record, book_type, lot_number, square, book, page)
    pob_text = point_of_beginning(lot_number, square)
    while True:
        write_file_name = input(f"Enter a file name for the Legal Description "
                                f"(the file will be saved here: {os.getcwd()}): ")
        if not re.search(r'[\\/*?:"<>|]', write_file_name):
            try:
                with open(write_file_name, 'w') as legal:
                    legal.write(being_clause_text + '\n\n')
                    legal.write(pob_text + '\n')
                    legal.write(courses + '\n')
                    legal.write(last_course)
                    break
            except IOError as e:
                print(f"Not able to open file {e}. Please try again. ")
        else:
            print("Invalid characters in file name.Please try again. ")


def being_clause(portion, record, book_type, lot_number, square, book, page):
    being_clause_header = f"""
DESCRIPTION OF
{portion.upper()} OF LOT {lot_number} IN SQUARE {square}
{book_type.upper()} {book}, PAGE {page}
WASHINGTON, D.C.\n"""

    being_clause_text = (f"\tBeing {portion} of Lot {lot_number} in Square {square}, as {record} in "
                         f"{book_type} {book} at Page {page} among the Records of the Office of the "
                         f"Surveyor of the District of Columbia and being more particularly described as follows:"
                         )
    being_text = being_clause_header + " \n" + textwrap.fill(being_clause_text, width=90)
    return being_text


def get_lot_data():
    while True:
        lot_type_valid_inputs = ['R', 'T']
        lot_type = input("Is this lot a record 'R' or tax 'T' lot? Enter R/T: ").upper()
        if lot_type in lot_type_valid_inputs:
            if lot_type == "R":
                record = "recorded"
                book_type = "Subdivision Book"
            else:
                record = "filed"
                book_type = "Assessment and Taxation Book"
            while True:
                try:
                    lot_number = int(input("Enter lot number: "))
                    break
                except ValueError:
                    print("Invalid input. Enter a number: ")
            # square can have a suffix N-E-S-W
            square = input("Enter square number (include suffix): ")
            # the book can be alphanumeric:
            book = input(f"Enter the {book_type}: ")
            page = input(f"Enter {book_type} Page: ")
            return record, book_type, lot_number, square, book, page
        else:
            print("Invalid input. Please enter R or T: ")


def point_of_beginning(lot_number, square):

    begin = "Beginning for the same at a point"
    while True:
        valid_inputs = ['Y', 'N']
        square_line_choice = input("Is the P.O.B. on the square's outline (including the corners)? Enter Y/N: ").upper()
        if square_line_choice in valid_inputs:
            while True:
                if square_line_choice == "Y":
                    square_corner_choice = input("Is the P.O.B. at a square corner? Enter Y/N: ").upper()
                    if square_corner_choice in valid_inputs:
                        # Point of Beginning is a square corner/ intersection of two streets
                        if square_corner_choice == "Y":
                            point_quadrant, first_street, second_street = get_point_quadrant(
                                point="Which square corner is the P.O.B.")
                            street_name, street_width = get_street(first_street)
                            street_name_second, street_width_second = get_street(second_street)
                            pob_text = (
                                f"\t{begin} marking the {point_quadrant} corner "
                                f"of the aforesaid Lot {lot_number} in Square {square}, said point also marking the "
                                f"intersection of the {first_street} line of {street_name} ({street_width}) and the "
                                f"{second_street} line of {street_name_second} ({street_width_second}); thence leaving "
                                f"the aforesaid {point_quadrant} corner of Lot {lot_number} in Square {square} and "
                                f"running for the following courses and distances:"
                            )
                            pob = textwrap.fill(pob_text, width=90) + "\n"
                            return pob
                        # Point of Beginning is a Lot corner on a square line
                        else:
                            pob_lot_corner = input("Is the Point of Beginning a lot corner? Enter Y/N: ").upper()
                            if pob_lot_corner in valid_inputs:
                                if pob_lot_corner == "Y":
                                    point_quadrant, first_street, second_street = get_point_quadrant(
                                        point="Which lot corner is the P.O.B.")
                                    lot_line, street_line = get_line_quadrant()
                                    street_name, street_width = get_street(street_line)
                                    pob_text = (
                                        f"\t{begin} marking the {point_quadrant} corner of "
                                        f"the aforesaid Lot {lot_number} in Square {square}, said point also lying on "
                                        f"the {street_line} line of {street_name} ({street_width}); thence leaving the "
                                        f"{point_quadrant} corner of Lot {lot_number} in Square {square} and running "
                                        f"for the following courses and distances:"
                                    )
                                    pob = textwrap.fill(pob_text, width=90) + "\n"
                                    return pob
                                # Point of Beginning is on a square line/lot line but not a square corner.
                                else:
                                    point_quadrant, first_street, second_street = get_point_quadrant(
                                        point="Which lot corner will be used as a tie")
                                    lot_line, street_line = get_line_quadrant()
                                    street_name, street_width = get_street(street_line)
                                    distance = get_distance(
                                        count="Enter the distance between the lot corner used as a tie and the P.O.B: ")
                                    bearing = get_bearing(count="")
                                    pob_first_paragraph = (
                                        f"\t{begin} lying on the {street_line} line of "
                                        f"{street_name} ({street_width}), said point also lying on the {lot_line} line "
                                        f"of the aforesaid Lot {lot_number} in Square {square}, said point being the "
                                        f"following course and distance from the {point_quadrant} corner of the "
                                        f"aforesaid Lot {lot_number} in Square {square}; thence leaving said "
                                        f"{point_quadrant} corner and running with a portion of the common line of Lot "
                                        f"{lot_number} in Square {square} and {street_name}"
                                    )
                                    pob_tie = (
                                        f"{bearing}, {distance} feet (record) to the True Point of Beginning; thence "
                                        f"running so as to cross and include a portion of the aforesaid Lot "
                                        f" {lot_number} in Square {square} the following courses and distances: "
                                    )
                                    pob = (
                                            textwrap.fill(pob_first_paragraph, width=90) + " \n"
                                            + textwrap.fill(pob_tie, width=90) + " \n"
                                    )
                                    return pob
                            else:
                                print("Invalid input. Enter Y/N: ")
                    else:
                        print("Invalid input. Enter Y/N: ")

                # Point of Beginning is inside a Square
                else:
                    while True:
                        pob_lot_line = input(
                            "Is the P.O.B. on a lot outline (including the corners)? Enter Y/N: ").upper()
                        if pob_lot_line in valid_inputs:
                            if pob_lot_line == "Y":
                                while True:
                                    pob_lot_corner = input("Is the P.O.B. the corner of a Lot. Enter Y/N: ").upper()
                                    if pob_lot_corner in valid_inputs:
                                        # Point of Beginning is the corner of a lot inside the square
                                        if pob_lot_corner == "Y":
                                            point_quadrant, first_street, second_street = get_point_quadrant(
                                                point="Which lot corner is the Point of Beginning")
                                            pob_text = (
                                                f"\t{begin} marking the {point_quadrant} "
                                                f"corner of the aforesaid Lot {lot_number} in Square {square}; thence "
                                                f"leaving said {point_quadrant} corner of Lot {lot_number} in Square "
                                                f"{square} and running for the following courses and distances: "
                                            )
                                            pob = textwrap.fill(pob_text, width=90) + " \n"
                                            return pob
                                        # Point of Beginning on Lot line with tie to the lot corner
                                        else:
                                            print("The P.O.B. is on a lot line, a tie to a lot corner required...")
                                            lot_line, street_line = get_line_quadrant()
                                            point_quadrant, first_street, second_street = get_point_quadrant(
                                                point="Which lot corner will be used as a tie")
                                            distance = get_distance(
                                                count="Enter the distance from the lot corner to P.O.B: ")
                                            bearing = get_bearing(count="")
                                            pob_text = (
                                                f"\t{begin} lying on the {lot_line} line of "
                                                f"the aforesaid Lot {lot_number} in Square {square}, said point being "
                                                f"the following course and distance from the {point_quadrant} corner "
                                                f"of the aforesaid Lot {lot_number} in Square {square}\n "
                                                f"\n{bearing}, {distance} feet (record) to the True Point of Beginning "
                                                f"; thence running so as to cross and include a portion of the "
                                                f"aforesaid Lot {lot_number} in Square {square} the following courses "
                                                f"and distances: "
                                            )
                                            pob = textwrap.fill(pob_text, width=90) + " \n"
                                            return pob

                                    else:
                                        print("Invalid input. Enter Y or N: ")

                            # Point of Beginning inside the Lot
                            else:
                                print("\n"
                                      "The True Point of Beginning is inside the lot. Two ties to a lot corner "
                                      "are required...")
                                point_quadrant, first_street, second_street = get_point_quadrant(
                                    point="Which lot corner"
                                          " will be used as a tie to Point of Beginning.")
                                first_distance = get_distance(count="Enter first tie distance from the lot corner: ")
                                first_bearing = get_bearing(count="first")
                                second_distance = get_distance(
                                    count="Enter second tie distance starting from the lot corner: ")
                                second_bearing = get_bearing(count="second")
                                pob_text = (
                                    f"\t{begin} lying within the aforesaid Lot {lot_number} "
                                    f"in Square {square}, said point being the following two (2) courses and distances "
                                    f"from the {point_quadrant} corner of said Lot {lot_number} in Square {square}; "
                                    f"thence leaving said {point_quadrant} corner and running so as to cross a portion "
                                    f"of Lot {lot_number} in Square {square}"
                                )
                                pob_tie = (
                                    f"{first_bearing}, {first_distance} feet (record) to a point; thence \n"
                                    f"{second_bearing}, {second_distance} feet (record) to the True Point of Beginning "
                                    f"; thence running so as to cross and include a portion of the aforesaid Lot "
                                    f" {lot_number} in Square {square} the following courses and distances: "
                                )
                                pob = textwrap.fill(pob_text, width=90) + " \n" + pob_tie + " \n"
                                return pob
                        else:
                            print("Invalid input. Enter Y or N: ")
        else:
            print("Invalid input. Enter Y or N: ")


def get_distance(count):
    while True:
        distance = input(f"{count}")
        try:
            distance = float(distance)
            return distance
        except ValueError:
            print("Input the distance (two decimals): ")


def get_street(street_order):
    street_name = input(f"The P.O.B. is on the {street_order} line of a street. Enter street name: ")
    street_width_choice = input("Enter street width or enter 'V' for variable width: ").upper()
    if street_width_choice == 'V':
        street_width = "variable width public street"
    else:
        street_width = f"{street_width_choice} foot wide public street"
    return street_name, street_width


def get_point_quadrant(point):
    quad_valid_inputs = ['NE', 'SE', 'SW', 'NW']
    while True:
        corner_quad = input(f"{point} Enter NE, SE, SW, NW: ").upper()
        if corner_quad in quad_valid_inputs:

            if corner_quad == "NE":
                corner_quad = "northeasterly"
                first_street = "southerly"
                second_street = "westerly"
                return corner_quad, first_street, second_street
            elif corner_quad == "NW":
                corner_quad = "northwesterly"
                first_street = "southerly"
                second_street = "easterly"
                return corner_quad, first_street, second_street
            elif corner_quad == "SW":
                corner_quad = "southwesterly"
                first_street = "northerly"
                second_street = "easterly"
                return corner_quad, first_street, second_street
            elif corner_quad == "SE":
                corner_quad = "southeasterly"
                first_street = "northerly"
                second_street = "westerly"
                return corner_quad, first_street, second_street
        else:
            print("Invalid input. Enter 'NE' for northeasterly, 'SE' for southeasterly, 'SW' for southeasterly or "
                  "'NW' for northwesterly: ")


def get_line_quadrant():

    line_quad_valid_inputs = ['N', 'E', 'S', 'W']
    while True:
        line_quadrant = input(f"On which Lot line is the Point of Beginning located: northerly, easterly, southerly "
                              f"or westerly. Enter N/E/S/W ").upper()
        if line_quadrant in line_quad_valid_inputs:
            if line_quadrant == "N":
                lot_line = "northerly"
                street_line = "southerly"
                return lot_line, street_line
            elif line_quadrant == "E":
                lot_line = "easterly"
                street_line = "westerly"
                return lot_line, street_line
            elif line_quadrant == "S":
                lot_line = "southerly"
                street_line = "northerly"
                return lot_line, street_line
            elif line_quadrant == "W":
                lot_line = "westerly"
                street_line = "easterly"
                return lot_line, street_line
        else:
            print("Invalid input. Enter (N) for northerly, (E) for easterly, (S) for southerly , (W) for westerly ")


def get_bearing_quadrants(count):
    quad_valid_inputs = ['N', 'E', 'S', 'W', 'NE', 'SE', 'SW', 'NW']
    while True:
        bearing_quad = input(f"Enter {count} bearing direction: N, NE, E, SE, S, SW, W, NW: ").upper()
        if bearing_quad in quad_valid_inputs:
            if bearing_quad == "N":
                first_bearing_quadrant = "Due"
                second_bearing_quadrant = "North"
                return first_bearing_quadrant, second_bearing_quadrant
            elif bearing_quad == "E":
                first_bearing_quadrant = "Due"
                second_bearing_quadrant = "East"
                return first_bearing_quadrant, second_bearing_quadrant
            elif bearing_quad == "S":
                first_bearing_quadrant = "Due"
                second_bearing_quadrant = "South"
                return first_bearing_quadrant, second_bearing_quadrant
            elif bearing_quad == "W":
                first_bearing_quadrant = "Due"
                second_bearing_quadrant = "West"
                return first_bearing_quadrant, second_bearing_quadrant
            elif bearing_quad == "NE":
                first_bearing_quadrant = "North"
                second_bearing_quadrant = "East"
                return first_bearing_quadrant, second_bearing_quadrant
            elif bearing_quad == "NW":
                first_bearing_quadrant = "North"
                second_bearing_quadrant = "West"
                return first_bearing_quadrant, second_bearing_quadrant
            elif bearing_quad == "SW":
                first_bearing_quadrant = "South"
                second_bearing_quadrant = "West"
                return first_bearing_quadrant, second_bearing_quadrant
            elif bearing_quad == "SE":
                first_bearing_quadrant = "South"
                second_bearing_quadrant = "East"
                return first_bearing_quadrant, second_bearing_quadrant
        else:
            print("Invalid input. Enter 'N' for North, 'E' for East, 'S' for South, 'W' for West, 'NE' for Northeast, "
                  "'SE' for Southeast, 'SW' for Southwest or 'NW' for Northwest")


def get_bearing(count):
    first_bearing_quadrant, second_bearing_quadrant = get_bearing_quadrants(count)
    if first_bearing_quadrant == "Due":
        bearing = f"{first_bearing_quadrant} {second_bearing_quadrant}"
    else:
        while True:
            try:
                degrees_bearing = int(input("Input bearing degrees: "))
                break
            except ValueError:
                print("Invalid input. Enter a two digits number: ")
        while True:
            try:
                minutes_bearing = int(input("Input bearing minutes: "))
                break
            except ValueError:
                print("Invalid input. Enter a two digits number: ")
        while True:
            try:
                seconds_bearing = int(input("Input bearing seconds: "))
                break
            except ValueError:
                print("Invalid input. Enter a two digits number: ")

        bearing = (
            f"{first_bearing_quadrant} {degrees_bearing}\u00b0 {minutes_bearing}' {seconds_bearing}\" "
            f"{second_bearing_quadrant}"
        )
    return bearing


def metes_bounds(data):
    """
    Calculate the bearing and distance between consecutive points in a csv file.
    Parameters:
    data (list): A list of coordinates where each coordinate is a tuple of (northing, easting).
    Returns:
    list: A list of tuples where each tuple contains the bearing and distance between consecutive points.
    """
    results = []
    for i in range(len(data) - 1):
        north, east = delta(data, i)
        distance = calculate_distance(north, east)
        bearing = calculate_bearing(north, east)
        results.append((bearing, distance))
    return results


def read_csv():
    """
    This function prompts the user for a file name. It checks if the file exists and if it's a .csv or .txt file.
    If the file is empty, it informs the user and prompts for another file.
    If the file is not empty, it reads the file and stores the data in a list.
    """
    while True:
        csv_file = input("Enter the CSV file name: ")
        if os.path.isfile(csv_file):
            while True:
                if csv_file.endswith(".csv") or csv_file.endswith(".txt"):
                    try:
                        with open(csv_file, 'r') as file:
                            reader = csv.reader(file)
                            csv_list = []
                            if os.stat(csv_file).st_size == 0:
                                print("The file is empty. Please try again. ")
                                break
                            for row in reader:
                                if len(row) > 3:
                                    raise ValueError("Too many columns in the CSV file. Please try again ")
                                elif len(row) < 3:
                                    raise ValueError(f"One or more rows contains only {len(row)} columns. Please try "
                                                     f"again")
                                csv_list.append(row)
                            first_row = csv_list[0]
                            csv_list.append(first_row)
                            # raise a ValueError for less than 3 points.
                            if len(csv_list) <= 3:
                                raise ValueError(f"The {csv_file} contains only {len(csv_list) - 1} points. A minimum "
                                                 f"of 3 points required. Please try again")
                            else:
                                return csv_list
                    except FileNotFoundError:
                        print("File not found. Please try again.")
                else:
                    print("Not a .txt or .csv file. Enter the csv file name. Include the extension .csv or .txt: ")
                    break
        else:
            print(f"No such '{csv_file}' file in directory: '{os.getcwd()}'. Please try again. ")


def delta(data, i):
    """
    This function calculates the difference in the north and east values between two consecutive data points. It uses
    the Decimal class for precise arithmetic :param data: A list of data points, where each point is a list with at
    least three elements, and the second and third elements are the north and east values, respectively. :param i:
    The index of the first data point in the data list. :return: A tuple containing the difference in the north and
    east values between the data point at index i and the data point at index i+1.
    """
    delta_north = Decimal(data[i + 1][1]) - Decimal(data[i][1])
    delta_east = Decimal(data[i + 1][2]) - Decimal(data[i][2])
    return delta_north, delta_east


def calculate_distance(delta_north, delta_east):
    """
    This function calculates the distance between two points
    :param delta_north:The difference in northing value between two points.
    :param delta_east:The difference in easting values between two points.
    :return: A string representing the calculated distance, formatted to two decimals.
    """
    distance = round(math.sqrt((delta_north ** 2) + (delta_east ** 2)), 2)
    return "{:.2f}".format(distance)


def calculate_angle(delta_north, delta_east):
    """
        This function calculates the angle in degrees, minutes, and seconds (DMS) given the north and east deltas.
        It uses the Decimal class for precise arithmetic and handles ZeroDivisionError exceptions.
        :parameter delta_north: The difference in the north values between two points.
        :parameter delta_east: The difference in the east values between two points.
        :return: A tuple representing the calculated angle in DMS format.
        """
    try:
        getcontext().prec = 28
        angle_decimal = float(Decimal(delta_east) / Decimal(delta_north))
        angle_degrees = math.degrees(math.atan(angle_decimal))
        degrees = int(angle_degrees)
        degrees_dms = abs(degrees)
        decimal_minutes = (angle_degrees - degrees) * 60
        minutes = int(decimal_minutes)
        minutes_dms = abs(minutes)
        seconds_dms = round(abs((decimal_minutes - minutes) * 60))
        # If the seconds value is greater than 59.5, reset it to 0 and increment the minutes value
        if seconds_dms > 59.5:
            seconds_dms = 0
            minutes_dms += 1
            # If the minutes value is now 60 or more, reset it to 0 and increment the degrees value
            if minutes_dms >= 60:
                minutes_dms = 0
                degrees_dms += 1
        return degrees_dms, minutes_dms, seconds_dms
    # delta_east = 0
    except ZeroDivisionError:
        # used in calculate_bearing() to return "Due West"
        if delta_east < 0:
            return 270, 0, 0
        # used in calculate_bearing() to return "Due East"
        if delta_east > 0:
            return 90, 0, 0
        # # used in calculate_bearing() to raise an exception when both delta_north and delta_east are zero.
        if delta_north == 0 and delta_east == 0:
            return 360, 0, 0


def calculate_bearing(delta_north, delta_east):
    degrees_dms, minutes_dms, seconds_dms = calculate_angle(delta_north, delta_east)
    # except ZeroDivisionError from calculate_angle()
    if degrees_dms == 270 and minutes_dms == 0 and seconds_dms == 0:
        return "Due West"
    elif degrees_dms == 180 and minutes_dms == 0 and seconds_dms == 0:
        return "Due East"
    elif degrees_dms == 360 and minutes_dms == 0 and seconds_dms == 0:
        raise Exception("Both delta_north and delta_east are zero. Check .csv file for a duplicate point of the same "
                        "corner ")
    # close to 90 degrees or 0 cases
    elif degrees_dms == 0 and minutes_dms == 0 and seconds_dms == 0:
        if delta_north > 0:
            return "Due North"
        elif delta_north < 0:
            return "Due South"
    elif degrees_dms == 90 and minutes_dms == 0 and seconds_dms == 0:
        if delta_east == 0:
            return "Due East"
        elif delta_east > 0:
            return "Due East"
        elif delta_east < 0:
            return "Due West"
    elif delta_north < 0 and delta_east < 0:
        return f"South {str(degrees_dms).zfill(2)}\u00B0{str(minutes_dms).zfill(2)}'{str(seconds_dms).zfill(2)}\" West"
    elif delta_north < 0 and delta_east > 0:
        return f"South {str(degrees_dms).zfill(2)}\u00B0{str(minutes_dms).zfill(2)}'{str(seconds_dms).zfill(2)}\" East"
    elif delta_north < 0 and delta_east == 0:
        return "Due South"
    elif delta_north > 0 and delta_east < 0:
        return f"North {str(degrees_dms).zfill(2)}\u00B0{str(minutes_dms).zfill(2)}'{str(seconds_dms).zfill(2)}\" West"
    elif delta_north > 0 and delta_east > 0:
        return f"North {str(degrees_dms).zfill(2)}\u00B0{str(minutes_dms).zfill(2)}'{str(seconds_dms).zfill(2)}\" East"
    elif delta_north > 0 and delta_east == 0:
        return "Due North"
    elif delta_north == 0 and delta_east == 0:
        raise Exception(
            "Both delta_north and delta_east are zero. Check .csv file for duplicate point of the same corner ")


def calculate_area(data):
    """
    Calculates the area of a polygon using Shoelace formula, given the northing and easting coordinates. :parameter:
    data(list): A list of tuples, each containing the x and y coordinates of a vertex of the polygon in order.
    :return: A tuple where the first element is the area of the polygon and the second element is the area converted
    to acres.
    """
    areas_list = []
    data.append(data[0])
    for i in range(len(data) - 2):
        shoelace_formula = (float(data[i][1]) * float(data[i + 1][2])) - (float(data[i + 1][1]) * float(data[i][2]))
        areas_list.append(shoelace_formula)
    area_square_feet = round(abs(sum(areas_list) / 2))
    area = "{:,}".format(area_square_feet)
    # acres are calculated from rounded area in square feet
    acres = round((area_square_feet / 43560), 5)
    data.pop()
    return area, acres


if __name__ == "__main__":
    main()
