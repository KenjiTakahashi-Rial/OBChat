"""
StringId enum container module.
Do not modify this file directly. It is generated from OB.strings.strings_generator.
"""

class StringId:
    """
    IDs used to get strings the string map (see OB.strings.strings_map).
    """

    # pylint: disable=line-too-long
    # Justification: This is just storage, it does not need to be readable.
    Invalid = "!@#$%^&*()"
    SystemUsername = "OB-Sys"
    AnonPrefix = "OB-Anon-"
    AnonBanning = "You're not even logged in! Try making an account first, then we can talk about banning people."
    NonAdminBanning = "That's a little outside your pay-grade. Only admins may ban users. Try to /apply to be an Admin."
    BanSyntax = "Usage: /ban <user1> <user2> ..."
    UserNotPresent = "Nobody named {0} in this room. Are you seeing things?"
    BanSelf = "You can't ban yourself. Just leave the room. Or put yourself on time-out."
    TargetOwner = "That's the owner. You know, your BOSS. Nice try."
    AlreadyBanned = "That user is already banned. How unoriginal of you."
    Admin = "Admin"
    JustLikeYou = " just like you"
    Unlimited = "Unlimited "
    BanPeer = "{0} is an {1}, so you can't ban them. Feel free to /elevate your complaints to someone who has more authority."
    BanSenderReceiptPreface = "Banned:"
    BanSenderReceiptNote = "That'll show them."
    BanOccupantsNotificationPreface = "One or more users have been banned:"
    BanOccupantsNotificationNote = "Let this be a lesson to you all."
    AnonElevating = "Why don't you make an account or log in first? Call us old-fashioned, but anons have very little privileges around these parts."
    NonAdminElevating = "Elevation is a skill that only Admins are capable of wielding. You have yet to reach the level of Admin - come back when you're ready!"
    ElevateSyntax = "Usage: /elevate (<command> <arg1> <arg2> ...) (<user1> <user2> ...) (<message>)"
    ElevateSelf = "You can't elevate to yourself. Who do you think you are?"
    ElevatePeer = "{0} does not have more privileges than you. What's the point of /elevate -ing to them?"
    ElevateSenderReceiptPreface = "Sent an elevation request:"
    ElevateTargetsNotificationPreface = "Received an elevation request from {0}"
    Recipients = "Recipients:"
    CommandRequested = "Command requested:"
    Message = "Message:"
