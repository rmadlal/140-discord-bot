import discord
import json
import sys

CONFIG = 'config.json'
_140 = '140'
_140_EMOJI_ID = 447884638049009686
_140_IRL_CHANNEL_ID = 329682110019534849


class Bot(object):

    def __init__(self):
        self._load_config()
        self._client = discord.Client()
        self._140_emoji = None

        @self._client.event
        async def on_ready():
            self._140_emoji = self._client.get_emoji(_140_EMOJI_ID)

        @self._client.event
        async def on_message(message):
            """
            React to a message containing '140' or posted in #140_irl with attachments
            with the 140 emoji.
            """
            if not self._should_act(message.author):
                return
            if not (_140 in message.content or (message.channel.id == _140_IRL_CHANNEL_ID and message.attachments)):
                return
            try:
                print(f'Sending reaction on message: {message}')
                await message.add_reaction(self._140_emoji)
            except discord.DiscordException as e:
                print(f'Reaction failed: {str(e)}', file=sys.stderr)

        @self._client.event
        async def on_reaction_add(reaction, user):
            """ Add a 140 emoji reaction to a message that just got one. """
            if not self._should_act(user):
                return
            if reaction.emoji != self._140_emoji:
                return
            try:
                print(f'Adding reaction to message: {reaction.message}')
                await reaction.message.add_reaction(self._140_emoji)
            except discord.DiscordException as e:
                print(f'Reaction failed: {str(e)}', file=sys.stderr)

    def _load_config(self):
        config = json.load(open(CONFIG))
        self._token = config['token']

    def _should_act(self, user):
        return not (user == self._client.user or self._140_emoji is None)

    def run(self):
        self._client.run(self._token)


def main():
    Bot().run()


if __name__ == '__main__':
    main()
