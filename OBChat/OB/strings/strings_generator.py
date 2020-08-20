"""
Script that generate the string ID module from strings.csv
"""

# TODO: Consider transferring from .csv to .json first for multiple locale support.

from csv import reader

# pylint: disable=invalid-name
# Justification: This is a script, so the variables do not need to be UPPER_SNAKE_CASE
string_id_module = open("string_id.py", "w")

string_id_module.write("\n".join([
    "\"\"\"",
    "StringId enum container module.",
    "Do not modify this file directly. It is generated from OB.strings.strings_generator.",
    "\"\"\"",
    "",
    "from enum import Enum",
    "",
    "class StringId(Enum):",
    "    \"\"\"",
    "    IDs used to get strings the string map (see OB.strings.strings_map).",
    "    \"\"\"",
    ""
]))

strings_spreadsheet = open("strings.csv", "r")

csv_reader = reader(strings_spreadsheet)
# The first row is just column headers
next(csv_reader)

i = 0

for row in csv_reader:
    # The ID is the 0th element, the English string is the 1st
    string_id_module.write(f"    {row[0]} = \"{row[1]}\"\n")
    i += 1

strings_spreadsheet.close()

print(f"{i} strings generated.")

string_id_module.close()
