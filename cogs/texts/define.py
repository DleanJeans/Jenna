import const
import json

from ..common import colors
from ..common import embed_limit
from ..common import utils
from discord.ext import commands
from urllib.parse import quote


API = 'https://api.dictionaryapi.dev/api/v2/entries/{}/{}'
GOOGLE_URL = 'https://www.google.com/search?q=define+'

WORD = 'word'
PHONETIC = 'phonetic'
MEANINGS = 'meanings'
PART_OF_SPEECH = 'partOfSpeech'
DEFINITIONS = 'definitions'
DEFINITION = 'definition'
EXAMPLE = 'example'
SYNONYMS = 'synonyms'
ORIGIN = 'origin'

NO_DEFS = 'No definitions found for this word.'
NO_DEFS_FOOTER = 'or there has been some problems with Google Dictionary. Try again later!'
FULL_FOOTER = 'To see more definitions, examples, synonyms and origins, type '

GOOGLE_DICTIONARY = 'Google Dictionary'

downloaded = {}

async def define(lang, word, full=False):
    url = API.format(lang, word)
    if downloaded.get(word):
        data = downloaded[word]
    else:
        data = await utils.download(url)
        data = json.loads(data or '{}')
        downloaded[word] = data

    embed = colors.embed(title=word, url=GOOGLE_URL + quote(word))
    embed.set_author(name=GOOGLE_DICTIONARY)
    if not isinstance(data, list):
        embed.description = NO_DEFS
        embed.set_footer(text=NO_DEFS_FOOTER)
        return embed
    
    for d in data:
        for meaning in d[MEANINGS]:
            lines = []
            phonetic = d.get(PHONETIC)
            part_of_speech = meaning.get(PART_OF_SPEECH)
            title = ' - '.join(filter(None, [phonetic, part_of_speech]))

            defs = meaning[DEFINITIONS]
            if not full:
                defs = [de for de in defs if de.get(DEFINITION)]
                defs = defs[:3]
            for i, de in enumerate(defs):
                if not de: continue
                numbering = f'{i+1}. ' if len(defs) > 1 else ''
                new_lines = []
                new_lines += [numbering + de.get(DEFINITION, '')]
                
                example = de.get(EXAMPLE)
                if full and example:
                    new_lines += [f'*"{example}"*']
                
                synonyms = de.get(SYNONYMS, [])
                has_synonyms = len(''.join(synonyms))
                if full and has_synonyms:
                    new_lines += [f'**{SYNONYMS.title()}**: ' + ' • '.join(f'`{s}`' for s in synonyms)]
                    new_lines += ['']
                
                lines, title = add_field_if_overflown(embed, title, lines, new_lines)
                lines += new_lines
            
            origin = d.get(ORIGIN)
            if full and origin:
                origin_line = [f'**{ORIGIN.title()}**: {origin}\n']
                lines, title = add_field_if_overflown(embed, title, lines, origin_line)
                lines += origin_line
            add_lines_as_field(embed, title, lines)
    return embed

def add_field_if_overflown(embed, title, lines, new_lines):
    value = '\n'.join(lines + new_lines)
    if len(value) > embed_limit.FIELD_VALUE:
        add_lines_as_field(embed, title, lines)
        title = const.INVISIBLE
        return [], title
    return lines, title

def add_lines_as_field(embed, title, lines):
    value = '\n'.join(lines)
    embed.add_field(name=title, value=value, inline=False)

SUPPORTED_LANGS = {
    'en': 'English',
    'hi': 'Hindi',
    'es': 'Spanish',
    'fr': 'French',
    'ja': 'Japanese',
    'ru': 'Russian',
    'de': 'German',
    'it': 'Italian',
    'ko': 'Korean',
    'pt-BR': 'Brazilian Portuguese',
    'zh-CN': 'Chinese (Simplified)',
    'ar': 'Arabic',
    'tr': 'Turkish',
}

def DefinedLang(lang):
    if lang not in SUPPORTED_LANGS:
        raise commands.BadArgument('Language not supported')
    return lang

def Full(s):
    if s.lower() != 'full':
        raise commands.BadArgument('Not Full')
    return True
    