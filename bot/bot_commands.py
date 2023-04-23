from nio import AsyncClient, MatrixRoom, RoomMessageText

from bot.chat_functions import react_to_event, send_text_to_room
from bot.config import Config
from bot.storage import Storage
from bot.emoji import make_many_emoji

from essential_generators import MarkovTextGenerator

class Command:
    def __init__(
        self,
        client: AsyncClient,
        store: Storage,
        config: Config,
        command: str,
        room: MatrixRoom,
        event: RoomMessageText,
    ):
        """A command made by a user.

        Args:
            client: The client to communicate to matrix with.

            store: Bot storage.

            config: Bot configuration parameters.

            command: The command and arguments.

            room: The room the command was sent in.

            event: The event describing the command.
        """
        self.client = client
        self.store = store
        self.config = config
        self.command = command
        self.room = room
        self.event = event
        self.args = self.command.split()[1:]
        self.wonky_word_bot = MarkovTextGenerator()

        

    async def process(self):
        """Process the command"""
        if self.command.startswith("echo"):
            await self._echo()
        elif self.command.startswith("react"):
            await self._react()
        elif self.command.startswith("status"):
            await self._status()
        elif self.command.startswith("speak"):
            await self._speak()
        elif self.command.startswith("mute"):
            await self._mute()
        elif self.command.startswith("unmute"):
            await self._unknown_command()
        elif self.command.startswith("help"):
            await self._show_help()
        else:
            await self._unknown_command()

    async def _echo(self):
        """Echo back the command's arguments"""
        response = " ".join(self.args)
        await send_text_to_room(self.client, self.room.room_id, response)

    async def _react(self):
        """Make the bot react to the command message"""
        # React with a start emoji
        
        for reaction in make_many_emoji(50):
            await react_to_event(
                self.client, self.room.room_id, self.event.event_id, reaction
            )
        
        # React with some generic text
        reaction = self.wonky_word_bot.gen_text(3)
        await react_to_event(
            self.client, self.room.room_id, self.event.event_id, reaction
        )

    async def _show_help(self):
        """Show the help text"""
        if not self.args:
            text = (
                f"🤖 Hello, I am a {self.config.bot_name}! Use `help commands` to view available commands. 😎"
            )
            await send_text_to_room(self.client, self.room.room_id, text)
            return

        topic = self.args[0]
        if topic == "rules":
            text = self.config.rules
        elif topic == "commands":
            text = "Available commands: help, react, echo, status, speak, mute, unmute"
        else:
            text = "Unknown help topic!"
        await send_text_to_room(self.client, self.room.room_id, text)

    async def _unknown_command(self):
        await send_text_to_room(
            self.client,
            self.room.room_id,
            f"Unknown command '{self.command}'. Try the 'help' command for more information.",
        )

   
    async def _status(self):
        word_of_the_day = self.wonky_word_bot.gen_word()
        await send_text_to_room(
            self.client,
            self.room.room_id,
            f"🤖 Ahoy! The word of the day is: {word_of_the_day}",
        )

    async def _speak(self):
        wonky_word_bot = MarkovTextGenerator()
        await send_text_to_room(
            self.client,
            self.room.room_id,
            f"🤖 {wonky_word_bot.gen_text(11)}",
        )

    async def _mute(self):
        self.event.sender
        user = self.event.body.lower().split(" ")[1]
        sender = self.event.sender
        if not sender in self.config.admins:
            await send_text_to_room(
                self.client,
                self.room.room_id,
                f"🤖 Hey Now! {sender} you aint suposed to do that 🫣",
            )
            return None

        if user in self.config.muted_peeps:
            await send_text_to_room(
                self.client,
                self.room.room_id,
                f"🤖 {user} who dat?",
            )
        else:
            self.config.muted_peeps.append(user)
            await send_text_to_room(
                self.client,
                self.room.room_id,
                f"🤖 {user} has been 86'ed",
            )

    async def _unmute(self):
        self.event.sender
        user = self.event.body.lower().split(" ")[1]
        sender = self.event.sender
        if not sender in self.config.admins:
            await send_text_to_room(
                self.client,
                self.room.room_id,
                f"🤖 Hey Now! {sender} you aint suposed to do that 🫣",
            )
            return None

        try:
            self.config.muted_peeps.remove(user)
            await send_text_to_room(
                self.client,
                self.room.room_id,
                f"🤖 {user} is cool again",
            )
        except ValueError:
            self.config.muted_peeps.append(user)
            await send_text_to_room(
                self.client,
                self.room.room_id,
                f"🤖 {user} is already one of the cool kids",
            )