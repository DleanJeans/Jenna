import discord
import typing
import colors
import timedisplay
import const
import io
import cogs

from discord.ext import commands
from .core import utils

SAVE_LIMIT = 10
DELETED = 'deleted'
EDITED = 'edited'

class ChannelMessageLog:
    def __init__(self):
        self.deleted = []
        self.edited = []
    
    def get_list(self, state):
        return getattr(self, state)
    
    def log(self, state, message):
        msgs = self.get_list(state)
        msgs.append(message)
        msgs = msgs[-SAVE_LIMIT:]
        setattr(self, state, msgs)
    
    def log_deleted(self, message): self.log(DELETED, message)    
    def log_edited(self, message): self.log(EDITED, message)

    def get_last(self, state, index):
        try:
            return self.get_list(state)[-index]
        except:
            return None

class GuildMessageLog:
    def __init__(self):
        self.channels = {}
    
    def get_channel_log(self, channel):
        if channel.id not in self.channels:
            self.channels[channel.id] = ChannelMessageLog()
        return self.channels[channel.id]
    
    def log(self, state, message):
        channel = self.get_channel_log(message.channel)
        channel.log(state, message)

    def log_deleted(self, message): self.log(DELETED, message)
    def log_edited(self, message): self.log(EDITED, message)
    
    def get_last(self, channel, state, index=1):
        channel_log = self.get_channel_log(channel)
        return channel_log.get_last(state, index)

GUILDS = 'sniped_guilds'

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = {}
        self.files_of_message = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.Persist = self.bot.get_cog(cogs.PERSIST)
        await self.Persist.wait_until_loaded()
        self.guilds = self.Persist.get(GUILDS, {})
        self.Persist.set(GUILDS, self.guilds)
    
    @commands.command(hidden=True, aliases=['re'])
    @commands.guild_only()
    async def repeatedit(self, context, channel:typing.Optional[discord.TextChannel], i=1):
        channel = channel or context.channel
        msg = self.get_last_message(channel, EDITED, i)
        if msg:
            await context.send(msg.content, embed=msg.embeds[0] if msg.embeds else None)
        else:
            await context.send(embed=self.create_empty_embed(channel, EDITED))
    
    @commands.command()
    @commands.guild_only()
    async def snipe(self, context, channel:typing.Optional[discord.TextChannel], i=1):
        await self.send_message_in_embed(context, channel, DELETED, i)
    
    @commands.command()
    @commands.guild_only()
    async def snipedit(self, context, channel:typing.Optional[discord.TextChannel], i=1):
        await self.send_message_in_embed(context, channel, EDITED, i)

    async def send_message_in_embed(self, context, channel, state, index):
        channel = channel or context.channel
        msg = self.get_last_message(channel, state, index)

        embed = self.create_empty_embed(channel, state)
        await self.embed_message_log(embed, msg, state)
        files = await self.get_message_files_cache_if_inaccessible(msg, embed)

        await context.send(embed=embed, files=files)
        if msg and msg.embeds:
            await context.send(embed=msg.embeds[0])
    
    def get_last_message(self, channel, state, index):
        guild = self.guilds.get(channel.guild.id)
        msg = guild.get_last(channel, state, index) if guild else None
        return msg

    def create_empty_embed(self, channel, state):
        embed = colors.embed()
        embed.description = f'No {state} messages to snipe!'
        embed.set_author(name='#' + channel.name)
        return embed
    
    async def embed_message_log(self, embed, msg, state):
        if not msg: return

        embed.set_author(name=str(msg.author), icon_url=msg.author.avatar_url)
        embed.description = msg.content or msg.system_content or ''
        embed.timestamp = msg.created_at
        embed.set_footer(text=state.capitalize())
        
        if not msg.attachments: return

        url = msg.attachments[0].proxy_url
        embed.set_image(url=url)

        links = get_attachment_links(msg, 'Link')
        embed.description += '\n' + ' '.join(links)

    async def get_message_files_cache_if_inaccessible(self, msg, embed):
        accessible = embed.image and await utils.download(embed.image.url)
        if accessible: return []

        files = self.files_of_message.get(msg.id, [])
        return files
    
    @commands.command()
    @commands.guild_only()
    async def snipelog(self, context, channel:discord.TextChannel=None):
        await self.send_log_in_embed(context, channel or context.channel, DELETED)
    
    @commands.command()
    @commands.guild_only()
    async def editlog(self, context, channel:discord.TextChannel=None):
        await self.send_log_in_embed(context, channel or context.channel, EDITED)
    
    async def send_log_in_embed(self, context, channel, state):
        guild_log = self.guilds.get(context.guild.id)
        channel_log = guild_log.channels.get(channel.id) if guild_log else None

        embed = self.create_empty_embed(channel, state)
        self.embed_channel_logs(embed, channel_log, state)

        await context.send(embed=embed)

    def embed_channel_logs(self, embed, channel_log, state):
        if not channel_log: return

        last_msg = None
        last_time = None
        msgs = []
        for m in channel_log.get_list(state):
            extra = get_extra(m)
            time = get_time_display(m, state)

            msg = f'`{time}` {m.content} {extra}'
            if not last_msg or last_msg.author != m.author:
                msg = f'{m.author.mention} {msg}'
            msgs += [msg]

            last_msg = m
            last_time = time
        
        if msgs:
            footer = f'{state.capitalize()}'
            embed.set_footer(text=footer)
            embed.description = '\n'.join(msgs)

    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        if not msg.guild or msg.author == self.bot.user: return
        await self.log_message(msg)
    
    async def log_message(self, msg, cache_files=True):
        guild = self.get_guild_log(msg.guild)
        guild.log_deleted(msg)
        if not cache_files: return
        files = [await a.to_file(use_cached=True) for a in msg.attachments]
        if files:
            self.files_of_message[msg.id] = files

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild or before.author == self.bot.user: return
        await self.log_message(before, cache_files=False)
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, msgs):
        for m in msgs:
            await self.log_message(m)

    def get_guild_log(self, guild):
        if guild.id not in self.guilds:
            self.guilds[guild.id] = GuildMessageLog()
        return self.guilds[guild.id]

def get_extra(msg):
    extra = get_attachment_links(msg)
    for e in msg.embeds:
        num = str(i+1) if len(msg.embeds) > 1 else ''
        embed = f'[Embed{num}]'
        extra += [embed]
    return ' '.join(extra)

def get_attachment_links(msg, text='File'):
    links = []
    count = len(msg.attachments)
    for i, a in enumerate(msg.attachments):
        num = str(i+1) if count > 1 else ''
        link = f'[[{text}{num}]]({a.proxy_url})'
        links += [link]
    return links

def get_time_display(m, state):
    message_time = m.edited_at if state == EDITED and m.edited_at else m.created_at
    display_format = timedisplay.HOUR if timedisplay.is_today(message_time) else timedisplay.DAY_HOUR
    message_time = timedisplay.to_ict(message_time, display_format)
    return message_time

def setup(bot):
    bot.add_cog(Snipe(bot))