import discord
from discord.ext.commands.errors import BadArgument
import googletrans
import re

from discord.ext import commands
from urllib.parse import quote as urlquote

from cogs.common.api import googledict as api
from cogs.common.api.googledict import Translated, SUPPORTED_LANGS
from .language_pair import InvalidLanguageCode, LanguagePair, NotLanguagePairFormat

GOOGLE_TRANSLATE = 'Google Translate'
TRANSLATE_URL = 'https://translate.google.com/?sl={}&tl={}&text={}&op=translate'
NO_TEXT = 'The last message has no text'
NA = '?'
TRY_AGAIN = 'Cannot reach Google Translate! Try again in a few minutes!'
RETRIES = 3
EMOJI_REGEX = r'(<a*(:[^:\s]+:)\d+>)'


def to_language_pair(src2dest):
    return LanguagePair.from_string(src2dest)


async def translate(ctx, src2dest: LanguagePair, text: str):
    text = text or NO_TEXT

    processed = process_emojis_in_text(text)
    if type(processed) is Translated:
        processed.src, processed.dest = src2dest.as_list()
        return processed
    text = processed

    src, dest, text = get_src_dest_text_overrided_by_last_word_if_valid(src2dest, text)

    translated = Translated(NA, NA, text, TRY_AGAIN)
    for _ in range(RETRIES):
        translated = await api.translate(text, src=src, dest=dest)
        if both_src_dest_are_en(translated):
            src, dest = set_to_en_vi()
        else:
            return translated


def get_src_dest_text_overrided_by_last_word_if_valid(left_pair, text):
    try:
        last_word = text.split()[-1]
        right_pair = LanguagePair.from_string(last_word, use_default_if_empty=False)
        other_words = text[:text.rindex(' ')]
        return *left_pair.override(right_pair).as_list(), other_words
    except NotLanguagePairFormat:
        return *left_pair.as_list(), text
    except InvalidLanguageCode as e:
        raise BadArgument(str(e)) from e


def process_emojis_in_text(text):
    text_has_emojis = re.findall(EMOJI_REGEX, text)
    text_stripped_of_emojis = re.sub(EMOJI_REGEX, '', text).strip()
    text_has_only_emojis = text_has_emojis and text_stripped_of_emojis == ''

    if text_has_only_emojis:
        return create_result_with_cleaned_emojis(text)
    else:
        return text_stripped_of_emojis


def create_result_with_cleaned_emojis(text):
    text_with_cleaned_emojis = re.sub(EMOJI_REGEX, r'\2', text)
    translated = Translated(None, None, text, text_with_cleaned_emojis)
    return translated


def both_src_dest_are_en(translated):
    return translated.src == translated.dest == 'en'


def set_to_en_vi():
    return 'en', 'vi'


ICON = 'https://upload.wikimedia.org/wikipedia/commons/d/db/Google_Translate_Icon.png'


async def embed_translate(ctx, src2dest, text):
    translated = await translate(ctx, src2dest, text)

    translate_url = TRANSLATE_URL.format(translated.src, translated.dest,
                                         urlquote(translated.origin))
    embed = discord.Embed(color=0x4a88ed)
    embed.set_author(name=GOOGLE_TRANSLATE, url=translate_url, icon_url=ICON)

    src_lang_and_code = get_language_and_code_in_brackets(translated.src)
    dest_lang_and_code = get_language_and_code_in_brackets(translated.dest)
    embed.add_field(name=f'{src_lang_and_code}', value=enclose_in_codeblock(translated.origin))
    embed.add_field(name=f'{dest_lang_and_code}', value=enclose_in_codeblock(translated.text))

    return embed


def get_language_and_code_in_brackets(code):
    code = code.lower()
    return f'{SUPPORTED_LANGS[code].title()} ({code})'


def enclose_in_codeblock(text: str):
    return f'```{text}```'


def get_supported_languages():
    output = '**Supported Languages**:\n'
    output += '\n'.join(
        [f'`{code}`-{lang.title()}' for code, lang in googletrans.LANGUAGES.items()])
    return output