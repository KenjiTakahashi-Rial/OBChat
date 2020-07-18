"""
Description:
    DeleteTest class container module.
"""

from pytest import mark

from OB.tests.test_commands.base import BaseCommandTest

class DeleteTest(BaseCommandTest):
    """
    Description:
        Class to test the /delete command function (see OB.commands.owner_level.delete).
    """

    def __init__(self):
        """
        Description:
            Declares the instance variables that be used for testing, includes communicators and
            database objects.
        """

        super().__init__(unlimited_admins=2, limited_admins=2, auth_users=2, anon_users=2)

    @mark.asyncio
    @mark.django_db()
    async def tests(self):
        """
        Description:
            Tests the /delete command (see OB.commands.owner_level.delete).
        """
