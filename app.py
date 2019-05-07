import discord
import json

CONFIG = 'config.json'
ONEFORTY = '140'


class Bot(object):

    def __init__(self):
        self._config = json.load(open(CONFIG))
        self._client = discord.Client()
        self._140_emoji = None

        @self._client.event
        async def on_ready():
            print(f'Connected to {self._client.guilds}')

        @self._client.event
        async def on_message(message):
            if message.author == self._client.user:
                return
            if message.content.find(ONEFORTY) == -1:
                return
            if self._140_emoji is None:
                self._140_emoji = next((e for e in await message.guild.fetch_emojis() if e.name == ONEFORTY), None)
                if self._140_emoji is None:
                    # Why am I here? I have no purpose in this server.
                    return
            print(f'Sending reaction on message: {message.content}')
            await message.add_reaction(self._140_emoji)

    def run(self):
        self._client.run(self._config['token'])


def main():
    Bot().run()


if __name__ == '__main__':
    main()
