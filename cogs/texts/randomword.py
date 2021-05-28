from urllib.parse import quote as url_quote
from bs4 import BeautifulSoup
from ..common import utils

GOOGLE_URL = 'https://www.google.com/search?hl=en&safe=on&q={0}&oq={0}&aq=f&aqi=&aql=&gs_sm=s'
URL = 'https://randomword.com/'
IDIOM = 'Idiom'
WORD = 'word'

def get_google_url(word):
    return GOOGLE_URL.format(url_quote(word))

async def get_random_word():
    return get_random()

async def get_random_idiom():
    return get_random(IDIOM)

async def get_random(what=''):
    what = what.lower()
    if what == WORD:
        what = ''
    url = URL + what
    web_content = await utils.download(url)
    soup = BeautifulSoup(web_content, 'html.parser')
    word = soup.find(id='random_word').text
    definition = soup.find(id='random_word_definition').text

    return word, definition