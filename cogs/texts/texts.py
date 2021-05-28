import const
import googletrans
import re
import upsidedown

from . import define
from . import palabrasaleatorias as pa
from . import randomword
from . import translate as gtranslate
from ..common import colors
from ..common import converter as conv
from ..common import utils
from ..common import unscramble
from ..emotes.const import EMOJI_PATTERN
from discord.ext import commands
from typing import Optional


class Texts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = googletrans.Translator()
    
    @commands.command(aliases=['usd'])
    async def upsidedown(self, ctx, *, text):
        text = text.replace('||', '')
        text = upsidedown.transform(text)
        await ctx.send(text)
    
    @commands.command(aliases=['usb'], hidden=True)
    async def unscramble(self, ctx, *, text):
        await ctx.trigger_typing()
        anagrams = await unscramble(text)
        response = f'`{text}` → '
        if anagrams:
            response += ' '.join([f'`{a}`' for a in anagrams])
        else:
            response += 'Not found!'
        await ctx.send(response)
    
    @commands.command(aliases=['str'])
    async def saytranslate(self, ctx, src2dest:Optional[gtranslate.Src2Dest]='auto>en', *, text=None):
        await ctx.trigger_typing()
        text, ref_message = utils.get_ref_message_text_if_no_text(ctx, text)
        text, last_message = await utils.get_last_message_text_if_no_text(ctx, text)
        translated = await gtranslate.translate(ctx, src2dest, text)
        where = ref_message or last_message or ctx
        await where.reply(translated.text, mention_author=False)
    
    @commands.group(aliases=['tr', 'tl'], invoke_without_command=True)
    async def translate(self, ctx, src2dest:Optional[gtranslate.Src2Dest]='auto>en', *, text=None):
        await ctx.trigger_typing()
        text, _ = utils.get_ref_message_text_if_no_text(ctx, text)
        text, _ = await utils.get_last_message_text_if_no_text(ctx, text)
        embed = await gtranslate.embed_translate(ctx, src2dest, text)
        await ctx.send(embed=embed)

    @translate.command(name='langs', aliases=['lang'])
    async def translatelangs(self, ctx):
        output = gtranslate.get_supported_languages()
        await ctx.message.author.send(output)
        await utils.emotes.react_tick(ctx.message)

    @commands.command(aliases=['rdw'])
    async def randomword(self, ctx, lang='en'):
        await ctx.trigger_typing()
        if lang == 'en':
            await self.send_random(ctx)
        else:
            word, definitions = await pa.get_random(lang)
            embed = colors.embed(title=word)
            embed.set_author(name=pa.get_title(lang), url=pa.get_url(lang))
            embed.description = const.BULLET.join([f'[[{site}]]({url})' for site, url in definitions.items()])
            await ctx.send(embed=embed)

    async def send_random(self, ctx, what='Word'):
        word, definition = await randomword.get_random(what)
        url = randomword.get_google_url(word)
        embed = colors.embed(title=word, url=url, description=definition)
        embed.set_author(name=f'Random {what}', url=randomword.URL)
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['rdi'])
    async def randomidiom(self, ctx):
        await self.send_random(ctx, randomword.IDIOM)

    @commands.group(aliases=['def', 'df'], invoke_without_command=True)
    async def define(self, ctx, full:Optional[define.Full]=False, lang:Optional[define.DefinedLang]='en', *, word):
        command = ctx.message.content.split()
        command.insert(2, 'full')
        command = ' '.join(command)
        embed = await define.define(lang, word, full)
        await ctx.send(embed=embed)
    
    @define.command(name='langs', aliases=['lang'])
    async def dictlangs(self, ctx):
        languages = '\n'.join([f'`{code}` - {lang}' for code, lang in define.SUPPORTED_LANGS.items()])
        response = 'Google Dictionary supported languages:\n' + languages
        await ctx.send(response)
    
    @commands.command(aliases=['s'])
    async def say(self, ctx, *, text):
        Emotes = self.bot.get_cog('Emotes')

        for plain_emoji in set(re.findall(EMOJI_PATTERN, text)):
            name = plain_emoji.strip(':')
            emoji_code = conv.get_known_emoji(self.bot.emojis, name)
            if not emoji_code:
                emoji_code = await Emotes.get_external_emoji(ctx, name, add=True)
                if not emoji_code: continue
            text = text.replace(plain_emoji, str(emoji_code))
        
        await ctx.send(text)


def setup(bot):
    bot.add_cog(Texts(bot))