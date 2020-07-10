"""
Class to test the /fire command function (see OB.commands.unlimited_admin_level.fire).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.tests.test_commands.base import BaseCommandTest

class FireTest(BaseCommandTest):
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
            Tests the /fire command (see OB.commands.unlimited_admin_level.fire).
        """
