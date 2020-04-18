"""
Storage for format functions that are called in multiple places and are not associated with any
particular instance of a class.
"""

from OB.constants import GroupTypes

def get_group_name(group_type, name, second_name=""):
    """
    Description:
        Gets the correctly formatted name of a group as a string.

    Arguments:
        group_type (GroupType): The type of the desired group name.
        name (string): The name of the target room or user of this group
        second_name (string): The name of the second target user. For private messages.

    Return values:
        A formatted group name string, if the GroupType was valid.
        Otherwise the name parameter's argument.
    """

    switch = {
        GroupTypes.Invalid:
            name,
        GroupTypes.Line:
            f"{name}_OB-Sys",
        GroupTypes.Room:
            f"room_{name}",
        GroupTypes.Private:
            f"{min(name, second_name)}_{max(name, second_name)}"
    }

    return switch[group_type]

def get_datetime_string(date_time):
    """
    Description:
        Gets the correctly formatted string for a datetime.
        Ensures consistent datetime format across the website.

    Arguments:
        date_time (datetime): The datetime to format as a string.

    Return values:
        A formatted datetime string.
    """

    # TODO: Find an elegant way to format the time for the client's timezone
    return date_time.strftime("%c")
