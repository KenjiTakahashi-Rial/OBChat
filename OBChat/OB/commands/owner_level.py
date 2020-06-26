"""
A user must be the owner of the room to perform these commands.
"""

from OB.utilities.event import send_system_room_message

async def delete(args, sender, room):
    """
    Description:
        Deletes an existing Room database object. All Admin, Ban, and Message objects will be
        deleted as well.

    Arguments:
        args (list[string]): The names of Rooms to delete. Should have length 1 or more.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """
    # TODO: Implement this
