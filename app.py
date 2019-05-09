import discord
import json
import sys

CONFIG = 'config.json'
_140_EMOJI_ID = 447884638049009686
_140_IRL_CHANNEL_ID = 329682110019534849
TEST_GUILD_ID = 575414432478527488
DEBUG = False


class Bot(object):

    def __init__(self):
        self._load_config()
        self._client = discord.Client()
        self._140_emoji = None
        self._on_message_conditions = {
            '140 in message': lambda message: '140' in message.content,
            '#140_irl attachment': lambda message: message.channel.id == _140_IRL_CHANNEL_ID and message.attachments
        }

        @self._client.event
        async def on_ready():
            self._140_emoji = self._client.get_emoji(_140_EMOJI_ID)

        @self._client.event
        async def on_message(message):
            """
            React with the 140 emoji to a message meeting one of the specified conditions.
            """
            if not self._should_act(message):
                return
            if not any(cond(message) for cond in self._on_message_conditions.values()):
                return
            try:
                print(f'Sending reaction on message: {message}')
                if DEBUG:
                    print('Condition(s) met: ' +
                          ', '.join(f'"{name}"' for name, cond in self._on_message_conditions.items() if cond(message)))
                await message.add_reaction(self._140_emoji)
            except discord.DiscordException as e:
                print(f'Reaction failed: {str(e)}', file=sys.stderr)

        @self._client.event
        async def on_reaction_add(reaction, _):
            """ Add a 140 emoji reaction to a message that just got one. """
            message = reaction.message
            if not self._should_act(message):
                return
            if reaction.me or reaction.emoji != self._140_emoji:
                return
            try:
                print(f'Adding reaction to message: {message}')
                await message.add_reaction(self._140_emoji)
            except discord.DiscordException as e:
                print(f'Reaction failed: {str(e)}', file=sys.stderr)

    def _load_config(self):
        config = json.load(open(CONFIG))
        self._token = config['token']

    def _should_act(self, message):
        return (not DEBUG or message.guild.id == TEST_GUILD_ID) \
               and message.author != self._client.user

    def run(self):
        self._client.run(self._token)


def main():
    global DEBUG
    if '-d' in sys.argv or '--debug' in sys.argv:
        DEBUG = True
    Bot().run()


if __name__ == '__main__':
    main()
