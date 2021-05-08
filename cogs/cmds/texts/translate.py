import colors
import googletrans
import re

from discord.ext import commands
from googletrans import LANGCODES, LANGUAGES, Translator

GOOGLE_TRANSLATE = 'Google Translate'
TRANSLATE_URL = 'https://translate.google.com/'
INVALID_LANG_CODE = '`{}` is not a language code. Type `{}translate langs` to see the full language codes. You can also use full language names.'
NO_TEXT = 'The last message has no text'
SUPPORTED_LANGS = { 'auto': 'Automatic', **LANGUAGES, **LANGCODES}

EMOJI_REGEX = '(<a*(:[^:\s]+:)\d+>)'
CUSTOM_DICT = {
    'nhoan': 'cringy',
}

translator = Translator()

class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

SRC2DEST_REGEX = '([\w-]*)>([\w-]*)'
def Src2Dest(s):
    if not re.match(SRC2DEST_REGEX, s):
        raise commands.BadArgument('Not in lang>lang format!')
    
    src, dest = re.findall(SRC2DEST_REGEX, s)[0]
    src = src or 'auto'
    dest = dest or 'en'
    return '>'.join([src, dest])

def try_parse_src2dest(s):
    try:
        return Src2Dest(s)
    except:
        return '>'

async def translate(context, src2dest, text):
    global translator
    text = await get_last_message_if_text_none(context, text)

    emojis_to_clean = re.findall(EMOJI_REGEX, text)
    for full, clean in emojis_to_clean:
        text = text.replace(full, '')

    src2dest = src2dest.lower().split('>')
    suffix_src2dest = try_parse_src2dest(text.split()[-1]).split('>')
    if suffix_src2dest:
        text = text[:text.rfind(' ')]
        suffix_src2dest = suffix_src2dest
    
    for lang in src2dest + suffix_src2dest:
        if lang and lang not in SUPPORTED_LANGS:
            raise commands.BadArgument(INVALID_LANG_CODE.format(lang, context.prefix))
    src, dest = src2dest
    src = suffix_src2dest[0] or src
    dest = suffix_src2dest[1] or dest

    translated = dotdict({ 
        'text': 'Google Translate stopped working! Try again later.',
        'src': '???',
        'dest': '???',
        'src2dest': ''
    })
    for i in range(5):
        try:
            translated = translator.translate(text, src=src, dest=dest)
            if translated.src == translated.dest == 'en':
                dest = 'vi'
            else:
                break
        except e:
            translator = Translator()
    
    translated.src2dest = f'{LANGUAGES[translated.src]}>{LANGUAGES[translated.dest]}'
    for word, meaning in CUSTOM_DICT.items():
        translated.text = translated.text.replace(word, meaning)
    
    return translated

async def embed_translate(context, src2dest, text):
    translated = await translate(context, src2dest, text)

    embed = colors.embed(description=translated.text)
    embed.set_author(name=GOOGLE_TRANSLATE, url=TRANSLATE_URL)
    embed.set_footer(text=f'{translated.src}>{translated.dest} ({translated.src2dest}):\n{text}')

    return embed

async def get_last_message_if_text_none(context, text):
    if not text:
        last_message = await context.history(limit=1, before=context.message).flatten()
        text = last_message[0].clean_content or translate.NO_TEXT
    return text

def get_supported_languages():
    output = '**Supported Languages**:\n'
    output += '\n'.join([f'`{code}`-{lang.title()}' for code, lang in googletrans.LANGUAGES.items()])
    return output