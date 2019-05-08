import discord
import json
import sys

CONFIG = 'config.json'
ONEFORTY = '140'


class Bot(object):

    def __init__(self):
        self._config = json.load(open(CONFIG))
        self._client = discord.Client()
        self._140_emoji = None

        @self._client.event
        async def on_ready():
            try:
                guild = await self._client.fetch_guild(184830159805743104)
                self._140_emoji = next((e for e in await guild.fetch_emojis() if e.name == ONEFORTY), None)
            except discord.DiscordException as e:
                print(f'Error: {str(e)}', file=sys.stderr)
                return

        @self._client.event
        async def on_message(message):
            if message.author == self._client.user:
                return
            if self._140_emoji is None:
                # Why am I here? I have no purpose in this server.
                return
            if message.content.find(ONEFORTY) == -1:
                return
            print(f'Sending reaction on message: {message.content}')
            try:
                await message.add_reaction(self._140_emoji)
            except discord.DiscordException as e:
                print(f'Reaction failed: {str(e)}', file=sys.stderr)

        @self._client.event
        async def on_reaction_add(reaction, user):
            if user == self._client.user:
                return
            if self._140_emoji is None or reaction.emoji != self._140_emoji:
                return
            print(f'Adding reaction')
            try:
                await reaction.message.add_reaction(self._140_emoji)
            except discord.DiscordException as e:
                print(f'Reaction failed: {str(e)}', file=sys.stderr)

    def run(self):
        self._client.run(self._config['token'])


def main():
    Bot().run()


if __name__ == '__main__':
    main()
