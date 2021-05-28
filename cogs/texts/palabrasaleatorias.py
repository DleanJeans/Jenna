from ..common import utils
from bs4 import BeautifulSoup
from discord.ext import commands

URL = 'https://www.palabrasaleatorias.com/'
PAGES_FOR_LANG = {
    'ar': 'kalimat-eashwayiya',
    'ca': 'paraula-aleatoria',
    'da': 'tilfaeldige-ord',
    'fi': 'satunnaiset-sanat',
    'fr': 'mots-aleatoires',
    'de': 'zufallige-worter',
    'nl': 'willekeurige-woorden',
    'it': 'parole-casuali',
    'pt': 'palavras-aleatorias',
    'es': 'index',
    'sv': 'slumpade-ord',
}
PHP = '.php'

def get_page(lang):
    return PAGES_FOR_LANG.get(lang)

def get_title(lang):
    page = get_page(lang) if lang != 'es' else 'palabras-aleatorias'
    title = ' '.join(page.split('-')).title()
    return title

def raise_if_not_supported(lang):
    if lang not in PAGES_FOR_LANG:
        raise commands.BadArgument(f'`{lang}` is not supported.')

def get_url(lang):
    page = get_page(lang)
    url = URL + page + PHP
    return url

async def get_random(lang):
    raise_if_not_supported(lang)
    url = get_url(lang)
    page_content = await utils.request(url)
    soup = BeautifulSoup(page_content, 'html.parser')
    table = soup.table
    word = table.div.text.strip()
    definitions = { a.text: a['href'] for a in table('a') }
    return word, definitions