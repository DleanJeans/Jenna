import requests_async
from dotmap import DotMap
from googletrans import LANGCODES, LANGUAGES

SUPPORTED_LANGS = {**LANGUAGES, **LANGCODES, 'auto': 'Automatic', '?': '?'}

API_URL_TEMPLATE = 'https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={}&tl={}&q={}'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67'
HEADERS_WITH_USER_AGENT = {'User-Agent': USER_AGENT}


class Translated:
    def __init__(self, src, dest, origin, text, data=None):
        self.src = src
        self.dest = dest
        self.origin = origin
        self.text = text
        self.data = data


async def translate(text, dest='en', src='auto'):
    url = build_url(text, dest, src)
    response = await requests_async.get(url, headers=HEADERS_WITH_USER_AGENT)
    data = DotMap(response.json())

    src = data.src
    origin = text
    text = ''.join(sentence.get('trans', '') for sentence in data.sentences if sentence)

    return Translated(src, dest, origin, text, data)


def build_url(text, dest, src):
    return API_URL_TEMPLATE.format(src, dest, text)