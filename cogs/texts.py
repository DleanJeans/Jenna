from discord.ext import commands
from .core.dank.unscramble import unscramble
from .cmds.texts import define
from .cmds.texts import translate as gtranslate
from .core.texts import palabrasaleatorias as pa
from .core.texts import randomword
from typing import Optional

import colors
import const
import discord
import googletrans
import re
import upsidedown

class Texts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = googletrans.Translator()
    
    @commands.command(aliases=['usd'])
    async def upsidedown(self, context, *, text):
        text = text.replace('||', '')
        text = upsidedown.transform(text)
        await context.send(text)
    
    @commands.command(aliases=['usb'], hidden=True)
    async def unscramble(self, context, *, text):
        await context.trigger_typing()
        anagrams = await unscramble(text)
        response = f'`{text}` → '
        if anagrams:
            response += ' '.join([f'`{a}`' for a in anagrams])
        else:
            response += 'Not found!'
        await context.send(response)
    
    @commands.command(aliases=['str'])
    async def saytranslate(self, context, src2dest:Optional[gtranslate.Src2Dest]='auto>en', *, text=None):
        await context.trigger_typing()
        translated = await gtranslate.translate(context, src2dest, text)
        await context.send(translated.text)
    
    @commands.group(aliases=['tr', 'tl'], invoke_without_command=True)
    async def translate(self, context, src2dest:Optional[gtranslate.Src2Dest]='auto>en', *, text=None):
        await context.trigger_typing()
        embed = await gtranslate.embed_translate(context, src2dest, text)
        await context.send(embed=embed)

    @translate.command(name='langs', aliases=['lang'])
    async def translatelangs(self, context):
        output = gtranslate.get_supported_languages()
        await context.message.author.send(output)
        await context.send('Supported Languages has been sent through DM!')

    @commands.command(aliases=['rdw'])
    async def randomword(self, context, lang='en'):
        await context.trigger_typing()
        if lang == 'en':
            await self.send_random(context)
        else:
            word, definitions = await pa.get_random(lang)
            embed = colors.embed(title=word)
            embed.set_author(name=pa.get_title(lang), url=pa.get_url(lang))
            embed.description = const.BULLET.join([f'[[{site}]]({url})' for site, url in definitions.items()])
            await context.send(embed=embed)

    async def send_random(self, context, what='Word'):
        word, definition = await randomword.get_random(what)
        url = randomword.get_google_url(word)
        embed = colors.embed(title=word, url=url, description=definition)
        embed.set_author(name=f'Random {what}', url=randomword.URL)
        await context.send(embed=embed)
    
    @commands.command(aliases=['rdi'])
    async def randomidiom(self, context):
        await self.send_random(context, randomword.IDIOM)

    @commands.group(aliases=['def', 'df'], invoke_without_command=True)
    async def define(self, context, full:Optional[define.Full]=False, lang:Optional[define.DefinedLang]='en', *, word):
        command = context.message.content.split()
        command.insert(2, 'full')
        command = ' '.join(command)
        embed = await define.define(lang, word, full)
        await context.send(embed=embed)
    
    @define.command(name='langs', aliases=['lang'])
    async def dictlangs(self, context):
        languages = '\n'.join([f'`{code}` - {lang}' for code, lang in define.SUPPORTED_LANGS.items()])
        response = 'Google Dictionary supported languages:\n' + languages
        await context.send(response)
    
    @commands.command()
    async def say(self, context, *, text):
        from .emotes import EMOJI_PATTERN
        Emotes = self.bot.get_cog('Emotes')

        for plain_emoji in set(re.findall(EMOJI_PATTERN, text)):
            name = plain_emoji.strip(':')
            emoji_code = Emotes.get_known_emoji(name)
            if not emoji_code:
                emoji_code = await Emotes.get_external_emoji(context, name, add=True)
                if not emoji_code: continue
            text = text.replace(plain_emoji, str(emoji_code))
        
        await context.send(text)


def setup(bot):
    bot.add_cog(Texts(bot))