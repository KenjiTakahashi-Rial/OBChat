"""
Communicator are used to test Consumers.

See the Django Channels documentation on Testing for more information.
https://channels.readthedocs.io/en/latest/topics/testing.html
"""

import json

import asyncio

from types import SimpleNamespace

from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator

from django.conf.urls import url

from OB.constants import GroupTypes
from OB.consumers import OBConsumer

class OBCommunicator(WebsocketCommunicator):
    def __init__(self, user, group_type, url_arg):
        """
        Description:
            Sets up the OBCommunicator to simulate an OBConsumer with the given arguments.
            Gives a placeholder "session" key for the scope because OBConsumer uses a session key to
            generate anonymous usernames.

        Arguments:
            user (OBUser): The user who will be assigned to the communicator's self.user.
            group_type (GroupType): Determines which type of group the communicator will connect to.
            url_arg (string): Either a room name or a username, depending on the group type.
        """

        if group_type == GroupTypes.Room:
            application = URLRouter([
                url(r"^chat/(?P<room_name>[-\w]+)/$", OBConsumer)
            ])
            super().__init__(application, f"/chat/{url_arg}/")
        elif group_type == GroupTypes.Private:
            application = URLRouter([
                url(r"^private/(?P<username>[-\w]+)/$", OBConsumer)
            ])
            super().__init__(application, f"/private/{url_arg}/")
        else:
            raise TypeError("OBCommunicator.__init__ received an invalid GroupType.")

        self.scope["user"] = user
        self.scope["session"] = SimpleNamespace(session_key=8)

    async def connect(self, timeout=1):
        """
        Description:
            Connects the OBCommunicator and tests that it connected without errors
        """

        is_connected, subprotocol = await super().connect()

        assert is_connected
        assert not subprotocol

        return self

    async def send(self, message_text):
        """
        Description:
            Sends a message in JSON format that OBConsumer uses.

        Arguments:
            message_text (string): The desired text to be sent.
        """

        message_json = json.dumps({"message_text": message_text})
        await self.send_to(text_data=message_json)

    async def receive(self, should_receive=True):
        """
        Description:
            Decodes a JSON message received by this OBCommunicator and returns the message text.
            If the frame received does not contain text, but contains a refresh signal, the refresh
            signal is returned as a dict.
            If the frame received contains neither text nor a refresh signal, the method attempts
            to receive another frame.

        Arguments:
            should_receive (bool): Indicates whether there should be something to receive. If
                False, ensures that a message is not received, otherwise raising an exception.

        Return Values:
            If text is received, the decoded text is returned.
            If a refresh signal is received, the refresh signal as a dict is returned.
            If the should_receive parameter is False, returns None.
        """

        if should_receive:
            while True:
                receipt = json.loads(await self.receive_from())

                # Return either the text or
                if "text" in receipt:
                    return receipt["text"]

                if "refresh" in receipt:
                    return receipt
        else:
            try:
                await self.receive_from()
                assert False
            except asyncio.TimeoutError:
                return False
