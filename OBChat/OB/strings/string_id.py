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
    BanOccupantsNotificationNote = "Fear the almighty ban-hammer."
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
    AnonKicking = "You're not even logged in! Try making an account first, then we can talk about kicking people."
    NonAdminKicking = "That's a little outside your pay-grade. Only admins may kick users. Try to /apply to be an Admin."
    KickSyntax = "Usage: /kick <user1> <user2> ..."
    KickSelf = "You can't kick yourself. Just leave the room. Or put yourself on time-out."
    KickPeer = "{0} is an {1}, so you can't kick them. Feel free to /elevate your complaints to someone who has more authority."
    KickSenderReceiptPreface = "Kicked:"
    KickSenderReceiptNote = "We'll see if they come back."
    KickOccupantsNotificationPreface = "One or more users have been kicked:"
    KickOccupantsNotificationNote = "Let this be a lesson to you all."
    AnonLifting = "You are far from one who can lift bans. Log in and prove yourself an Admin."
    NonAdminLifting = "A mere mortal like yourself does not have the power to lift bans. Try to /apply to be an Admin and perhaps you may obtain this power if you are worthy."
    LiftSyntax = "Usage: /lift <user1> <user2> ..."
    LiftInvalidTarget = "No user named {0} has been banned from this room. How can one lift that which has not been banned?"
    LiftInsufficientPermission = "{0} was banned by {1}. You cannot lift a ban issued by a user of equal or higher privilege than yourself. If you REALLY want to lift this ban you can /elevate to a higher authority."
    LiftSenderReceiptPreface = "Ban lifted:"
    LiftSenderReceiptNote = "Fully reformed and ready to integrate into society."
    AnonApplying = "You can't get hired looking like that! Clean yourself up and make an account first."
    UnlimitedAdminApplying = "You're already a big shot Unlimited Admin! There's nothing left to apply to."
    AdminSuffix = " [Admin]"
    User = "User: "
    Position = "Position:"
    ApplySenderReceiptPreface = "Application sent:"
    ApplySenderReceiptNote = "Hopefully the response doesn't start with: \"After careful consideration...\""
    ApplyTargetsNotificationPreface = "Application Received:"
    ApplyTargetsNotificationNote = "To hire this user, use /hire."
    AnonCreating = "Identify yourself! Must log in to create a room."
    CreateSyntax = "Usage: /create <name>"
    CreateSyntaxError = "Room name cannot contain spaces."
    CreateExistingRoom = "Someone beat you to it. {0} already exists."
    CreateSenderReceipt = "Sold! Check out your new room: {0}"
    NonOwnerDeleting = "Trying to delete someone else's room? How rude. Only the room owner may delete a room"
    DeleteSyntax = "Usage: /delete <room name> <owner username>"
    NonUnlimitedAdminFiring = "That's a little outside your pay-grade. Only Unlimited Admins may fire admins. Try to /apply to be Unlimited."
    FireSyntax = "Usage: /fire <user1> <user2> ..."
    FireUserNotPresent = "{0} does not exist. You can't fire a ghost... can you?"
    FireSelf = "You can't fire yourself. I don't care how bad your performance reviews are."
    FireNonAdmin = "{0} is just a regular ol' user, so you can't fire them. You can /kick or /ban them if you want."
    FirePeer = "{0} is an Unlimited Admin, so you can't fire them. Please direct all complaints to your local room owner, I'm sure they'll love some more paperwork to do..."
    FireSenderReceiptPreface = "Fired:"
    FireSenderReceiptNote = "It had to be done."
    FireOccupantsNotificationPreface = "One or more users have been fired:"
    FireOccupantsNotificationNote = "Those budget cuts are killer."
    FireTargetsNotificationNote = "Clean out your desk."
    NonUnlimitedAdminHiring = "That's a little outside your pay-grade. Only Unlimited Admins may hire admins. Try to /apply to be Unlimited."
    HireSyntax = "Usage: /hire <user1> <user2> ..."
    HireInvalidTarget = "{0} does not exist. Your imaginary friend needs an account before they can be an Admin."
    HireSelf = "You can't hire yourself. I don't care how good your letter of recommendation is."
    HireAnon = "{0} hasn't signed up yet. They cannot be trusted with the immense responsibility that is adminship."
    HireUnlimitedAdmin = "{0} is already an Unlimited Admin. There's nothing left to /hire them for."
    HireInsufficientPrivilege = "{0} is already an Admin. Only the owner may promote them to Unlimited Admin"
    HireSenderReceiptPreface = "Hired:"
    HireSenderReceiptNote = "Now for the three-month evaluation period"
    HireOccupantsNotificationPreface = "One or more users have been hired:"
    HireOccupantsNotificationNote = "Drinks on them!"
    HireTargetsNotificationNote = "With great power comes great responsibility."
    PrivateSyntax = "Usage: /private /<user> <message>"
    PrivateInvalidSyntax = "Looks like you forgot a \"/\" before the username. I'll let it slide."
    PrivateInvalidTarget = "{0} doesn't exist. Your private message will broadcasted into space instead."
    PrivateNoMessage = "No message specified. Did you give up at just the username?"
    WhoInvalidTarget = "{0} doesn't exist, so that probably means nobody is in there."
    WhoEmpty = "{0} is all empty!"
    WhoPreface = "Users in {0}:"
    OwnerSuffix = " [Owner]"
    YouSuffix = " [you]"
