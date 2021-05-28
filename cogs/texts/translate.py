import googletrans
import re

from ..common import colors
from discord.ext import commands
from googletrans import LANGCODES, LANGUAGES, Translator
from urllib.parse import quote

GOOGLE_TRANSLATE = 'Google Translate'
TRANSLATE_URL = 'https://translate.google.com/?sl={}&tl={}&text={}&op=translate'
INVALID_LANG_CODE = '`{}` is not a language code. Type `{}translate langs` to see the full language codes. You can also use full language names.'
NO_TEXT = 'The last message has no text'
SUPPORTED_LANGS = { 'auto': 'Automatic', **LANGUAGES, **LANGCODES, '???': '???'}

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

    src, dest = map(fix_zh, [src, dest])

    return '>'.join([src, dest])

def fix_zh(lang):
    lang = lang.replace('_', '-')
    if lang.startswith('zh') and lang not in SUPPORTED_LANGS:
        return 'zh-cn'
    return lang

def try_parse_src2dest(s):
    try:
        return Src2Dest(s)
    except:
        return '>'

async def translate(ctx, src2dest, text):
    global translator
    text = text or NO_TEXT

    emojis_to_clean = re.findall(EMOJI_REGEX, text)
    for full, clean in emojis_to_clean:
        text = text.replace(full, '')

    src2dest = src2dest.lower().split('>')
    suffix_src2dest = try_parse_src2dest(text.split()[-1]).split('>')
    if ''.join(suffix_src2dest):
        text = text[:text.rfind(' ')]
        suffix_src2dest = suffix_src2dest
    
    for lang in src2dest + suffix_src2dest:
        if lang and lang not in SUPPORTED_LANGS:
            raise commands.BadArgument(INVALID_LANG_CODE.format(lang, ctx.prefix))
    src, dest = src2dest
    src = suffix_src2dest[0] or src
    dest = suffix_src2dest[1] or dest

    translated = dotdict({ 
        'text': 'Google Translate stopped working! Try again later.',
        'src': '???',
        'dest': '???',
        'src2dest': ''
    })
    for i in range(3):
        try:
            translated = translator.translate(text, src=src, dest=dest)
            if translated.src == translated.dest == 'en':
                src = 'en'
                dest = 'vi'
            else:
                break
        except TypeError:
            raise commands.BadArgument('Too short to translate :(')
        except:
            translator = Translator()
    
    translated.src2dest = f'{SUPPORTED_LANGS[translated.src.lower()]}>{SUPPORTED_LANGS[translated.dest.lower()]}'
    for word, meaning in CUSTOM_DICT.items():
        translated.text = translated.text.replace(word, meaning)
    translated.original_text = text

    return translated

async def embed_translate(ctx, src2dest, text):
    translated = await translate(ctx, src2dest, text)

    translate_url = TRANSLATE_URL.format(translated.src, translated.dest, quote(text))
    embed = colors.embed(title=GOOGLE_TRANSLATE, url=translate_url, description=translated.text, color=0x4a88ed)
    embed.add_field(name=f'{translated.src2dest} ({translated.src}>{translated.dest}):', value=translated.original_text)

    return embed

def get_supported_languages():
    output = '**Supported Languages**:\n'
    output += '\n'.join([f'`{code}`-{lang.title()}' for code, lang in googletrans.LANGUAGES.items()])
    return output