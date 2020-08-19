"""
Script that generate the string ID module from strings.csv
"""

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
    "",
    "    Invalid = \"!@#$%&\"",
    ""
]))

for i in range(5):
    string_id_module.write(f"    String{i} = \"{i}\"\n")

print("5 strings generated.")

string_id_module.close()
