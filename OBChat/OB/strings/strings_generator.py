"""
Script that generates both the string_ids module and the strings_map module from strings.csv
"""

# pylint: disable=invalid-name
# Justification: This is a script, so the variables do not need to be UPPER_SNAKE_CASE
string_ids = open("string_ids.py", "w")

string_ids.write("\n".join([
    "\"\"\"",
    "StringId enum container module.",
    "Do not modify this file directly. It is generated from OB.strings.strings_generator.",
    "\"\"\"",
    "",
    "from enum import Enum",
    "",
    "class StringId(Enum):",
    "    \"\"\"",
    "    IDs used to get strings from strings_map.",
    "    \"\"\"",
    "",
    "    Invalid = None",
    ""
]))

for i in range(5):
    string_ids.write(f"    String{i} = None\n")

print("5 strings generated.")

string_ids.close()
