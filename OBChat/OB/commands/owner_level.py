from OB.utilities import send_system_room_message

def delete_room(args, user, room):
    """
    Description:
        Deletes an existing Room database object. All Admin, Ban, and Message objects will be
        deleted as well.

    Arguments:
        args (list[string]): The names of Rooms to delete. Should have length 1 or more.
        user (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was issued in.

    Return values:
        None
    """
    # TODO: Implement this
