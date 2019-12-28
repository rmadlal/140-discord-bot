import os
import sys
import logging
from discord import Client, Game, Status, Message, Reaction, DiscordException

DEBUG = False
_140_EMOJI_ID = 447884638049009686
_140_IRL_CHANNEL_ID = 329682110019534849
_140_GAME = Game('140')


class Bot:

    def __init__(self):
        self._client = Client(activity=_140_GAME, status=Status.dnd if DEBUG else Status.online)
        self._140_emoji = None
        self._on_message_conditions = {
            '140 in message': lambda message: '140' in message.content,
            '#140_irl attachment': lambda message: message.channel.id == _140_IRL_CHANNEL_ID and message.attachments
        }
        self._reaction_add_conditions = {
            '140 emoji': lambda reaction: reaction.emoji == self._140_emoji,
            '1, 4, 0 emojis in order': self._has_140_in_order
        }

        @self._client.event
        async def on_ready():
            self._140_emoji = self._client.get_emoji(_140_EMOJI_ID)

        @self._client.event
        async def on_message(message):
            await self._140_reaction(message, self._on_message_conditions)

        @self._client.event
        async def on_reaction_add(reaction, _):
            await self._140_reaction(reaction, self._reaction_add_conditions)

    @staticmethod
    def _get_message(model):
        if isinstance(model, Message):
            return model
        if isinstance(model, Reaction):
            return model.message
        return None

    @staticmethod
    def _has_140_in_order(reaction):
        one, four, zero = '1⃣', '4⃣', '0⃣'
        reaction_emojis = [reaction.emoji for reaction in reaction.message.reactions]
        try:
            return reaction_emojis.index(one) < reaction_emojis.index(four) < reaction_emojis.index(zero)
        except ValueError:
            return False

    def _should_respond(self, model):
        return (isinstance(model, Message) and model.author != self._client.user) \
            or (isinstance(model, Reaction) and not model.me)

    async def _140_reaction(self, model=None, conditions=None):
        conditions = conditions or {}
        if not self._should_respond(model):
            return
        if not any(cond(model) for cond in conditions.values()):
            return
        try:
            message = self._get_message(model)
            print(f'Adding reaction to message: {message}')
            await message.add_reaction(self._140_emoji)
            if DEBUG:
                print('Condition(s) met: ' + ', '.join(
                      f'"{name}"' for name, cond in conditions.items() if cond(model)))
        except DiscordException as e:
            print(f'Reaction failed: {e}', file=sys.stderr)

    def run(self):
        self._client.run(os.getenv('BOT_TOKEN'))


def main():
    global DEBUG
    if '-d' in sys.argv or '--debug' in sys.argv:
        DEBUG = True
        logging.basicConfig(level=logging.DEBUG)
    Bot().run()


if __name__ == '__main__':
    main()
