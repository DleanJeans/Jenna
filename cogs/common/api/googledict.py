import requests_async
from dotmap import DotMap
from googletrans import LANGCODES, LANGUAGES

SUPPORTED_LANGS = {**LANGUAGES, **LANGCODES, 'auto': 'Automatic', '?': '?'}

API_URL_TEMPLATE = 'https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={}&tl={}&q={}'


class Translated:
    def __init__(self, src, dest, origin, text, data=None):
        self.src = src
        self.dest = dest
        self.origin = origin
        self.text = text
        self.data = data


async def translate(text, dest='en', src='auto'):
    url = build_url(text, dest, src)
    response = await requests_async.get(url)
    data = DotMap(response.json())

    src = data.src
    origin = text
    text = data.sentences[0].trans

    return Translated(src, dest, origin, text, data)


def build_url(text, dest, src):
    return API_URL_TEMPLATE.format(src, dest, text)