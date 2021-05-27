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
from .core import embed_limit, utils
from .core.emotes import external, webhook
from .core.emotes.const import *
from discord.ext import commands
from typing import Optional, Union
from env import HOME_GUILD, EMOTES_BUFFER_GUILD
class Emotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.external_emojis = {}
        self.external_paginator = external.EmojiPaginator(self)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.React = self.bot.get_cog(cogs.REACT)
        self.Persist = self.bot.get_cog(cogs.PERSIST)
        await self.Persist.wait_until_loaded()
        self.external_emojis = self.Persist.get(EXTERNAL_EMOJIS, {})
        self.Persist.set(EXTERNAL_EMOJIS, self.external_emojis)

    @commands.command(aliases=['s'])
    async def spell(self, ctx, *, text):
        await spell(ctx, text)
    
    @commands.command(aliases=['rs'])
    async def reactspell(self, ctx, channel:Optional[discord.TextChannel], i:Optional[int]=1, *, text):
        ref_message = utils.get_referenced_message(ctx.message)
        message_to_react = ref_message or await self.count_message(ctx, None, channel, i)
        await reactspell(message_to_react, text)
        await utils.emotes.react_tick(ctx.message)

    @commands.group(aliases=['emoji'], hidden=True)
    async def emote(self, ctx): pass

    @commands.command(aliases=['big', 'jumbo'])
    async def enlarge(self, ctx, emoji:Optional[conv.NitroEmoji]):
        await ctx.trigger_typing()
        emoji = await self.get_emote_from_reference_or_last_message(ctx, emoji)
        if type(emoji) is not discord.Emoji:
            emoji = await self.get_external_emoji(ctx, emoji) or emoji
        url, single_url = utils.emotes.get_url(emoji)
        if isinstance(emoji, str) and emoji[0].isalpha():
            url = ''
        elif single_url and not await utils.download(url, utils.READ):
            url = single_url
        
        if url:
            await ctx.send(url)
        else:
            await ctx.message.add_reaction('⁉️')
    
    async def get_emote_from_reference_or_last_message(self, ctx, emoji):
        if not emoji:
            text, _ = utils.get_ref_message_text_if_no_text(ctx.message, emoji)
            emojis = re.findall(EMOJI_NAME_REGEX, text or '')

            if not emojis:
                text, _ = await utils.get_last_message_text_if_no_text(ctx, emojis)
                emojis = re.findall(EMOJI_NAME_REGEX, text or '')

            if emojis:
                emoji = emojis[0]
            else:
                raise commands.BadArgument('No emoji to zoom in!')
        return emoji
        
    async def get_external_emoji(self, ctx, name, add=False):
        id = self.external_emojis.get(name)
        if not id: return
        emoji = utils.emotes.expand(name, id)
        emoji = await utils.emotes.to_partial_emoji(ctx, emoji)
        if emoji and add:
            emoji = await self.add_emoji(emoji)
        return emoji

    @commands.command(aliases=['emojis'])
    async def emotes(self, ctx, page:int=1):
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
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['nitrojis'])
    async def nitrotes(self, ctx, page=1):
        await ctx.trigger_typing()
        embed = await self.external_paginator.get_page(ctx, page)
        await ctx.send(embed=embed)

    async def count_message(self, ctx, author, channel, i):
        channel = channel or ctx.channel
        counter = 1
        if type(author) == int:
            i = author
            author = None

        async for message in channel.history(limit=None, before=ctx.message):
            if author and message.author != author:
                continue
            if counter < i:
                counter += 1
                continue
            break
        return message

    @commands.command()
    async def drop(self, ctx, emoji:conv.NitroEmoji, author:Optional[Union[int, conv.FuzzyMember]], channel:Optional[discord.TextChannel], i:int=1):
        ref_message = utils.get_referenced_message(ctx.message)
        message = ref_message or await self.count_message(ctx, author, channel, i)
        
        external = None
        if isinstance(emoji, str):
            emoji = await self.get_external_emoji(ctx, emoji, add=True)
            external = emoji
        
        try:
            await message.add_reaction(emoji)
            await utils.emotes.react_tick(ctx.message)
        except:
            await ctx.message.add_reaction('⁉️')
        
        if external:
            await external.delete()
    
    async def add_emoji(self, emoji):
        return await self.bot.get_guild(EMOTES_BUFFER_GUILD).create_custom_emoji(name=emoji.name, image=await emoji.url.read())

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot: return
        ctx = await self.bot.get_context(msg)
        if ctx.command:
            return
        await self.cache_external_emojis(msg)
        
        if await utils.is_user_on_local(ctx):
            return
        await self.reply_emojis(msg)

    async def reply_emojis(self, msg):
        ctx = await self.bot.get_context(msg)
        matches = []
        for line in msg.content.splitlines():
            if not line.startswith(START_QUOTE):
                matches += re.findall(EMOJI_PATTERN, line)
                
        emojis = []
        externals = []

        for emoji in matches:
            name = emoji.replace(':', '')
            emoji = conv.get_known_emoji(self.bot.emojis, name, msg.author)
            if not emoji:
                emoji = await self.get_external_emoji(ctx, name, add=True)
                if not emoji: continue
                externals += [emoji]
            
            if emoji:
                emojis += [str(emoji)]
        
        if emojis:
            emojis = ''.join(emojis)
            await webhook.try_send(self, ctx, emojis)
        
        for e in externals:
            await e.delete()
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        emoji = reaction.emoji
        if isinstance(emoji, discord.PartialEmoji):
            self.external_emojis[emoji.name] = str(emoji)

    async def cache_external_emojis(self, msg):
        ctx = await self.bot.get_context(msg)
        emojis = re.findall(REAL_EMOJI_PATTERN, msg.content)
        emojis += [r.emoji for r in msg.reactions if isinstance(r.emoji, discord.PartialEmoji)]
        
        new_emotes = False

        for e in emojis:
            partial = await utils.emotes.to_partial_emoji(ctx, e) if isinstance(e, str) else e
            known = conv.get_known_emoji(self.bot.emojis, partial.name)
            if not known:
                id = utils.emotes.shorten(e)
                self.external_emojis[partial.name] = str(e)
                new_emotes = True
        
        if new_emotes:
            self.Persist.request_backup()

    @emote.command()
    @commands.is_owner()
    async def cache(self, ctx, message:discord.Message):
        before = self.external_emojis.copy()
        await self.cache_external_emojis(message)
        changes = []
        if self.external_emojis != before:
            before, after = map(set, [before.items(), self.external_emojis.items()])
            changes = after - before
        await ctx.send(f'Found `{len(changes)}` new emotes!')

    @emote.command()
    @commands.is_owner()
    async def scan(self, ctx, channel:typing.Union[discord.TextChannel, int]=None, limit:int=100):
        if isinstance(channel, int):
            channel = self.bot.get_channel(channel)
        channel = channel or ctx.channel
        count_before = len(self.external_emojis)

        async with ctx.typing():
            async for message in channel.history(limit=limit):
                contains_emojis = re.findall(REAL_EMOJI_PATTERN, message.content)
                if contains_emojis:
                    await self.cache_external_emojis(message)
        
        count_after = len(self.external_emojis)
        change = count_after - count_before
        await ctx.send(f'✅ Found `{change}` new emotes!')

    @emote.command()
    @commands.has_guild_permissions(manage_emojis=True)
    @commands.bot_has_guild_permissions(manage_emojis=True)
    async def add(self, ctx, url, name=None):
        response = '⁉️'
        async with ctx.typing():
            image = await download_image(url)
            if image:
                if not name:
                    name = 'emoji%04d' % random.randint(0, 9999)
                await ctx.guild.create_custom_emoji(name=name, image=image)
                response = conv.get_known_emoji(self.bot.emojis, name, ctx.author)
            await ctx.message.add_reaction(response)

async def download_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                return await r.read()

def setup(bot):
    bot.add_cog(Emotes(bot))