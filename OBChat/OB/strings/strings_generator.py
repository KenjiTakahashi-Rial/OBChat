"""
Script that generates both the string_ids module and the strings_map module from strings.csv
"""

string_ids = open("string_ids.py", "w")

string_ids.write("\n".join([
    "\"\"\"",
    "StringId enum container module.",
    "Do not modify this file directly. It is generated from OB.strings.strings_generator.",
    "\"\"\"",
    "",
    "from enum import IntEnum",
    "",
    "class StringId(IntEnum):",
    "    \"\"\"",
    "    IDs used to get strings from strings_map.",
    "    \"\"\"",
    "\n",
]))

for i in range(5):
    string_ids.write(f"    String{i}: {i},\n")

print("5 strings generated.")

string_ids.close()
