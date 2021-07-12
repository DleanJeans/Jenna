from googletrans.client import Translator
import asyncio
from aioify import aioify

AsyncTranslator = aioify(Translator)

translator: AsyncTranslator = None


async def translate(text, dest='en', src='auto'):
    global translator
    if not translator:
        translator = AsyncTranslator()
    return await translator.translate(text, dest, src)