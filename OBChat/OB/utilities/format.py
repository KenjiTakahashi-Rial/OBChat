"""
Storage for format functions that are called in multiple places and are not associated with any
particular instance of a class.
"""

from OB.constants import GroupTypes

def get_group_name(group_type, target_id, second_id=-1):
    """
    Description:
        Gets the correctly formatted name of a group as a string.

    Arguments:
        group_type (GroupType): The type of the desired group name.
        target_id (int): The id of the target room or user of this group
        second_id (int): The id of the second target user. For private messages.

    Return values:
        A formatted group name string, if the GroupType was valid.
        Otherwise the name parameter's argument.
    """

    switch = {
        GroupTypes.Invalid:
            target_id,
        GroupTypes.Line:
            f"{target_id}_OB-Sys",
        GroupTypes.Room:
            f"room_{target_id}",
        GroupTypes.Private:
            f"{min(target_id, second_id)}_{max(target_id, second_id)}"
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
