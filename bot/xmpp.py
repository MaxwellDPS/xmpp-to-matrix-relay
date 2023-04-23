from datetime import datetime
import logging

import slixmpp

from nio import (
    AsyncClient,
    InviteMemberEvent,
    JoinError,
    MatrixRoom,
    MegolmEvent,
    RoomGetEventError,
    RoomMessageText,
    UnknownEvent,
)

from bot.bot_commands import Command
from bot.chat_functions import make_pill, react_to_event, send_text_to_room
from bot.config import Config
from bot.message_responses import Message
from bot.storage import Storage

logger = logging.getLogger(__name__)


class xmpp(slixmpp.ClientXMPP):
    def __init__(self, client, config: Config):
        """
        Args:
            client: nio client used to interact with matrix.

            store: Bot storage.

            config: Bot configuration parameters.
        """
        self.config = config
        self.command_prefix = config.command_prefix
        self.client = client
        self.room = self.config.xmpp_matrix_relay_room

      
        slixmpp.ClientXMPP.__init__(self, self.config.xmpp_username, self.config.xmpp_password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self._message)


    async def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        await self.get_roster()
        self.plugin['xep_0045'].join_muc(self.config.xmpp_room,
                                         self.config.xmpp_nick,
                                         )
        await send_text_to_room(
            self.client,
            self.room,
            "[+] Beep Boop 🤖 Bot is Listening and Ready"
        )

    def _check_keywords(self, msg: str) -> bool:
        for keyword in self.config.keywords:
            if keyword.lower() in msg.lower():
                return True
        return False

    async def _message(self, msg):
        """
        Process incoming message stanzas from any chat room. Be aware
        that if you also have any handlers for the 'message' event,
        message stanzas may be processed by both handlers, so check
        the 'type' attribute when using a 'message' event handler.

        Whenever the bot's nickname is mentioned, respond to
        the message.

        IMPORTANT: Always check that a message is not from yourself,
                   otherwise you will create an infinite loop responding
                   to your own messages.

        This handler will reply to messages that mention
        the bot's nickname.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        #loop = asyncio.get_event_loop()
        if msg['mucnick'] != self.config.xmpp_nick:
            if self._check_keywords(msg['body']):
                if self.config.keyword_alerts:
                    prefix = self.config.alert_prefix
            else:
                prefix = ''

            if msg['mucnick'].lower() not in self.config.muted_peeps:
                await send_text_to_room(
                    self.client,
                    self.room,
                    f'{prefix}{msg["mucnick"]}: {msg["body"]}'
                )
                logging.info(datetime.now().strftime('%c') + '    ' + msg['body'])
            else:
                if prefix != '':
                    await send_text_to_room(
                        self.client,
                        self.room,
                        f'{prefix}{msg["mucnick"]}: {msg["body"]}'
                    )
                        


    
    
    
