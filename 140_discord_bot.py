import logging
import os
import sys
from typing import Final, Iterable, Optional

from discord import Client, Emoji, Game, Message, RawMessageUpdateEvent

from utils import ocr_from_url

TOKEN: Final = os.getenv('BOT_TOKEN')
_140_EMOJI_ID: Final = 447884638049009686
_140_IRL_CHANNEL_ID: Final = 329682110019534849


class Bot:

    def __init__(self):
        self._client = Client(activity=Game('140'))

        @self._client.event
        async def on_message(message: Message):
            if self._should_react_to_message(message):
                await message.add_reaction(self._140_emoji)

        @self._client.event
        async def on_raw_message_edit(payload: RawMessageUpdateEvent):
            message = await self._client.get_channel(payload.channel_id).fetch_message(payload.message_id)
            if self._should_react_to_message(message):
                await message.add_reaction(self._140_emoji)

    @property
    def _140_emoji(self) -> Optional[Emoji]:
        return self._client.get_emoji(_140_EMOJI_ID)

    @staticmethod
    def _potential_140_irl_sources(message: Message) -> Iterable[str]:
        for embed in message.embeds:
            if title := embed.title:
                yield title
            if description := embed.description:
                yield description
            if author := embed.author:
                yield author.name
            if footer := embed.footer:
                yield footer.text
        for embed in message.embeds:
            if image := embed.image:
                yield ocr_from_url(image.url)
            if thumbnail := embed.thumbnail:
                yield ocr_from_url(thumbnail.url)
        for attachment in message.attachments:
            if attachment.height or attachment.width:  # image or video
                yield ocr_from_url(attachment.url)

    def _should_react_to_message(self, message: Message):
        if message.author == self._client.user:
            return False
        if '140' in message.content:
            return True
        if message.channel.id == _140_IRL_CHANNEL_ID:
            if any('140' in s for s in self._potential_140_irl_sources(message)):
                return True
        return False

    def run(self):
        self._client.run(TOKEN)


def main():
    logging.basicConfig(level=logging.DEBUG if any(arg in ('-d', '--debug') for arg in sys.argv) else logging.ERROR)
    Bot().run()


if __name__ == '__main__':
    main()
