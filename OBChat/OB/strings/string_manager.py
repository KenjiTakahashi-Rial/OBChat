"""
StringManager class container module.
"""

from OB.strings import strings_map
from OB.string_ids import StringId

class StringManager():
    """
    Gets strings from a .csv and holds them in a dict for access by a StringId.
    """

    @staticmethod
    def get_string(string_id):
        """
        Tries to get a string from the static dict in strings_map.
        If the given string ID does not correspond to a string, returns a placeholder.

        Arguments:
            string_id (string or StringId): The StringId or name string of the StringId to look up.
        """

        try:
            if isinstance(string_id, StringId):
                return strings_map[string_id]

            if isinstance(string_id, str):
                return strings_map[hash(string_id)]

            raise ValueError(f"Cannot get string by {type(string_id)}")

        except KeyError:
            return strings_map[StringId.Invalid]
