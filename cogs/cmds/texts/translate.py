import colors
import googletrans
import re

from discord.ext import commands

GOOGLE_TRANSLATE = 'Google Translate'
TRANSLATE_URL = 'https://translate.google.com/'
INVALID_LANG_CODE = '`{}` is not a language code'
NO_TEXT = 'The last message has no text'
SUPPORTED_LANGS = { 'auto': 'Automatic', **googletrans.LANGUAGES, **googletrans.LANGCODES}

EMOJI_REGEX = '(<a*(:[^:\s]+:)\d+>)'
CUSTOM_DICT = {
    'nhoan': 'cringy',
}

translator = googletrans.Translator()

def Src2Dest(s):
    src2dest = s.split('>')
    if len(src2dest) != 2:
        raise commands.BadArgument('Not in lang>lang format!')
    
    src, dest = src2dest
    src = src or 'auto'
    dest = dest or 'en'
    return '>'.join([src, dest])

def translate(src2dest, text):
    global translator

    emojis_to_clean = re.findall(EMOJI_REGEX, text)
    for full, clean in emojis_to_clean:
        text = text.replace(full, clean)

    src2dest = src2dest.split('>')
    for lang in src2dest:
        if lang and lang not in SUPPORTED_LANGS:
            raise commands.BadArgument(INVALID_LANG_CODE.format(lang))
    src, dest = src2dest

    while True:
        try:
            translated = translator.translate(text, dest=dest, src=src)
            break
        except AttributeError as e:
            translator = googletrans.Translator()

    translated_text = translated.text
    for word, meaning in CUSTOM_DICT.items():
        translated_text = translated_text.replace(word, meaning)

    embed = colors.embed(description=translated_text)
    embed.set_author(name=GOOGLE_TRANSLATE, url=TRANSLATE_URL)
    embed.set_footer(text=f'{translated.src}>{translated.dest}: {text}')

    return embed