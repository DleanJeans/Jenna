import discord
import typing
import re
import aiohttp
import colors
import math
import random
import cogs
import env
import const
import io

from .cmds.emotes import spell, reactspell
from .core import converter as conv
from .core import embed_limit
from .core.emotes import external, utils
from discord.ext import commands
from typing import Optional

EMOTES_PER_PAGE = 25
EMOJI_PATTERN = '(:[^:\s]+:)(?!\d)'
REAL_EMOJI_PATTERN = '(<a*:[^:\s]+:\d+>)'
HOME_GUILD = 596171359747440657
EMBED_BACKCOLOR = 0x2f3136
START_QUOTE = '> '

EXTERNAL_EMOJIS = 'external_emojis'

class Emotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.external_emojis = {}
        self.external_paginator = external.EmojiPaginator(self)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.Persist = self.bot.get_cog(cogs.PERSIST)
        await self.Persist.wait_until_loaded()
        self.external_emojis = self.Persist.get(EXTERNAL_EMOJIS, {})
        self.Persist.set(EXTERNAL_EMOJIS, self.external_emojis)
    
    @commands.command(aliases=['s'])
    async def spell(self, context, *, text):
        await spell(context, text)
    
    @commands.command(aliases=['rs'])
    async def reactspell(self, context, channel:Optional[discord.TextChannel], i:Optional[int]=1, *, text):
        message = await self.count_message(context, None, channel, i)
        await reactspell(message, text)
        await context.message.add_reaction('✅')

    @commands.group(aliases=['emoji'], hidden=True)
    async def emote(self, context): pass

    @commands.command(aliases=['big'])
    async def enlarge(self, context, emoji:conv.NitroEmoji):
        await context.trigger_typing()
        emoji = await self.get_external_emoji(context, emoji) or emoji
        url, single_url = utils.get_url(emoji)
        if isinstance(emoji, str) and emoji[0].isalpha():
            url = ''
        elif single_url and not await utils.download(url, utils.READ):
            url = single_url
        
        if url:
            await context.send(url)
        else:
            await context.message.add_reaction('⁉️')
        
    async def get_external_emoji(self, context, name, add=False):
        id = self.external_emojis.get(name)
        if not id: return
        emoji = utils.expand(name, id)
        emoji = await utils.to_partial_emoji(context, emoji)
        if emoji and add:
            emoji = await self.add_emoji(emoji)
        return emoji

    @commands.command(aliases=['emojis'])
    async def emotes(self, context, page:int=1):
        home_guild = self.bot.get_guild(HOME_GUILD)
        embed = colors.embed()
        embed.set_author(name='Available Emotes')
        total_page = math.ceil(len(home_guild.emojis) / EMOTES_PER_PAGE)
        embed.set_footer(text=f'Page {page}/{total_page}')
        
        all_emojis = sorted(home_guild.emojis, key=lambda e: e.name)
        emojis = []
        start = EMOTES_PER_PAGE * (page - 1)
        end = EMOTES_PER_PAGE * page
        page_emojis = all_emojis[start:end]
        for e in page_emojis:
            emojis += [f'{e} `:{e.name}:`']
        embed.description = '\n'.join(emojis)
        await context.send(embed=embed)
    
    @commands.command(aliases=['nitrojis'])
    async def nitrotes(self, context, page=1):
        await context.trigger_typing()
        embed = await self.external_paginator.get_page(context, page)
        await context.send(embed=embed)

    async def count_message(self, context, author, channel, i):
        channel = channel or context.channel
        counter = 1
        async for message in channel.history(limit=None, before=context.message):
            if author and message.author != author:
                continue
            if counter < i:
                counter += 1
                continue
            break
        return message

    @commands.command()
    async def drop(self, context, emoji:conv.NitroEmoji, author:Optional[conv.FuzzyMember], channel:Optional[discord.TextChannel], i:int=1):
        message = await self.count_message(context, author, channel, i)
        
        external = None
        if isinstance(emoji, str):
            emoji = await self.get_external_emoji(context, emoji, add=True)
            external = emoji
        
        try:
            await message.add_reaction(emoji)
            await context.message.add_reaction('✅')
        except:
            await context.message.add_reaction('⁉️')
        
        if external:
            await external.delete()
    
    async def add_emoji(self, emoji):
        return await self.bot.get_guild(HOME_GUILD).create_custom_emoji(name=emoji.name, image=await emoji.url.read())

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user: return
        context = await self.bot.get_context(msg)
        if context.command:
            return
        await self.cache_external_emojis(msg)
        
        if env.LOCAL:
            return
        await self.reply_emojis(msg)
    
    def get_known_emoji(self, name):
        def added_by_me(e):
            return -1 if e.user == self.bot.user else self.bot.emojis.index(e)
        emojis = sorted(self.bot.emojis, key=added_by_me)
        return discord.utils.get(emojis, name=name)

    async def reply_emojis(self, msg):
        context = await self.bot.get_context(msg)
        matches = []
        for line in msg.content.splitlines():
            if not line.startswith(START_QUOTE):
                matches += re.findall(EMOJI_PATTERN, line)
                
        emojis = []
        externals = []

        for emoji in matches:
            name = emoji.replace(':', '')
            emoji = self.get_known_emoji(name)
            if not emoji:
                emoji = await self.get_external_emoji(context, name, add=True)
                if not emoji: continue
                externals += [emoji]
            
            if emoji:
                emojis += [str(emoji)]
        
        if emojis:
            emojis = ''.join(emojis)
            await msg.channel.send(emojis)
        
        for e in externals:
            await e.delete()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        emoji = reaction.emoji
        if isinstance(emoji, discord.PartialEmoji):
            self.external_emojis[emoji.name] = str(emoji)

    async def cache_external_emojis(self, msg):
        if msg.author.bot: return
        context = await self.bot.get_context(msg)
        emojis = re.findall(REAL_EMOJI_PATTERN, msg.content)
        emojis += [r.emoji for r in msg.reactions if isinstance(r.emoji, discord.PartialEmoji)]
        
        new_emotes = False

        for e in emojis:
            partial = await utils.to_partial_emoji(context, e) if isinstance(e, str) else e
            known = self.get_known_emoji(partial.name)
            if not known:
                id = utils.shorten(e)
                self.external_emojis[partial.name] = str(e)
                new_emotes = True
        
        if new_emotes:
            self.Persist.request_backup()

    @emote.command()
    @commands.is_owner()
    async def cache(self, context, message:discord.Message):
        before = self.external_emojis.copy()
        await self.cache_external_emojis(message)
        changes = []
        if self.external_emojis != before:
            before, after = map(set, [before.items(), self.external_emojis.items()])
            changes = after - before
        await context.send(f'Found `{len(changes)}` new emotes!')

    @emote.command()
    @commands.is_owner()
    async def scan(self, context, channel:typing.Union[discord.TextChannel, int]=None, limit:int=100):
        if isinstance(channel, int):
            channel = self.bot.get_channel(channel)
        channel = channel or context.channel
        count_before = len(self.external_emojis)

        async with context.typing():
            async for message in channel.history(limit=limit):
                contains_emojis = re.findall(REAL_EMOJI_PATTERN, message.content)
                if contains_emojis:
                    await self.cache_external_emojis(message)
        
        count_after = len(self.external_emojis)
        change = count_after - count_before
        await context.send(f'✅ Found `{change}` new emotes!')

    @emote.command()
    @commands.has_guild_permissions(manage_emojis=True)
    @commands.bot_has_guild_permissions(manage_emojis=True)
    async def add(self, context, url, name=None):
        response = '⁉️'
        async with context.typing():
            image = await download_image(url)
            if image:
                if not name:
                    name = 'emoji%04d' % random.randint(0, 9999)
                await context.guild.create_custom_emoji(name=name, image=image)
                response = self.get_known_emoji(name)
            await context.message.add_reaction(response)

async def download_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                return await r.read()

def setup(bot):
    bot.add_cog(Emotes(bot))