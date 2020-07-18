"""
A user must be the owner of the room to perform this command (see OB.models.Room &
OB.constants.Privilege).
"""

from OB.constants import Privilege
from OB.models import Admin, Ban, Message
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_delete, async_model_list, async_filter
from OB.utilities.event import send_room_event, send_system_room_message

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

    error_message = ""
    sender_privilege = await async_get_privilege(sender, room)

    # Check for initial errors
    if sender_privilege < Privilege.Owner:
        error_message = (
            "Trying to delete someone else's room? How rude. Only the room owner may delete a room"
        )
    elif args:
        error_message = (
            "Usage: /delete"
        )

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    # Kick all users
    for user in await async_model_list(room.occupants):
        kick_event = {
            "type": "kick",
            "target_id": user.id
        }
        await send_room_event(room.id, kick_event)

    # Delete all Admins
    for admin in await async_filter(Admin, room=room):
        await async_delete(admin)

    # Delete all Bans
    for ban in await async_filter(Ban, room=room):
        await async_delete(ban)

    # Delete all Messages
    for message in await async_filter(Message, room=room):
        await async_delete(message)

    # Delete the room
    await async_delete(room)