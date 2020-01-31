import asyncio
import logging
import os
import sys
import time
from collections import namedtuple
from operator import attrgetter
from threading import Thread
from typing import Callable, Final, Optional, Union

import schedule
from discord import Client, DiscordException, Emoji, Game, Message, RawReactionActionEvent, TextChannel, User

TOKEN: Final = os.getenv('BOT_TOKEN')
_140_EMOJI_ID: Final = 447884638049009686
_140_IRL_CHANNEL_ID: Final = 329682110019534849
RACES_CHANNEL_ID: Final = 187112305505468417
ZET_ID: Final = 123160659130056708
GAMEGUY_ID: Final = 93504619614834688

Reaction = namedtuple('ReactionFromRaw', ['emoji', 'message', 'user'])


class Bot:

    def __init__(self):
        self._client = Client(activity=Game('140'))

        self._on_message_conditions = [
            lambda message: '140' in message.content,
            lambda message: message.channel.id == _140_IRL_CHANNEL_ID and message.attachments
        ]
        self._on_reaction_add_conditions = [
            lambda reaction: self._140_emoji and reaction.emoji == self._140_emoji,
            self._has_140_in_order
        ]

        @self._client.event
        async def on_ready():
            Thread(target=self._ping_racers_every_day).start()

        @self._client.event
        async def on_message(message: Message):
            await self._140_reaction(message, *self._on_message_conditions)

        @self._client.event
        async def on_raw_reaction_add(payload: RawReactionActionEvent):
            reaction = await self._init_reaction_from_raw(payload)
            await self._140_reaction(reaction, *self._on_reaction_add_conditions)

    @property
    def _140_emoji(self) -> Optional[Emoji]:
        return self._client.get_emoji(_140_EMOJI_ID)

    @property
    def _races_channel(self) -> Optional[TextChannel]:
        return self._client.get_channel(RACES_CHANNEL_ID)

    @property
    def _zet(self) -> Optional[User]:
        return self._client.get_user(ZET_ID)

    @property
    def _gameguy(self) -> Optional[User]:
        return self._client.get_user(GAMEGUY_ID)

    @staticmethod
    def _has_140_in_order(reaction: Reaction) -> bool:
        one, four, zero = '1️⃣', '4️⃣', '0️⃣'
        reaction_emojis = [reaction.emoji for reaction in reaction.message.reactions]
        try:
            return reaction_emojis.index(one) < reaction_emojis.index(four) < reaction_emojis.index(zero)
        except ValueError:
            return False

    @staticmethod
    def _get_message(model: Union[Message, Reaction]) -> Message:
        if isinstance(model, Message):
            return model
        if isinstance(model, Reaction):
            return model.message

    async def _init_reaction_from_raw(self, payload: RawReactionActionEvent) -> Reaction:
        message = await self._client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        user = self._client.get_user(payload.user_id)
        return Reaction(payload.emoji, message, user)

    def _should_respond(self, model: Union[Message, Reaction]) -> bool:
        get_user = {Message: attrgetter('author'), Reaction: attrgetter('user')}[type(model)]
        return get_user(model) != self._client.user

    async def _140_reaction(self, model: Union[Message, Reaction] = None, *conditions: Callable):
        if not (self._should_respond(model) and any(cond(model) for cond in conditions)):
            return
        try:
            message = self._get_message(model)
            await message.add_reaction(self._140_emoji)
        except DiscordException as e:
            print(f'Reaction failed: {e}', file=sys.stderr)

    def _ping_racers_every_day(self):
        # wrap Channel.send() in a non-async function because schedule doesn't work with async
        def send(message):
            asyncio.run_coroutine_threadsafe(self._races_channel.send(message), self._client.loop)

        schedule.every().day.at('16:00'). \
            do(send, f'{self._zet.mention} {self._gameguy.mention} will you two race already?!')

        while True:
            schedule.run_pending()
            time.sleep(60)

    def run(self):
        self._client.run(TOKEN)


def main():
    logging.basicConfig(level=logging.DEBUG if '-d' in sys.argv or '--debug' in sys.argv else logging.ERROR)
    Bot().run()


if __name__ == '__main__':
    main()
