import discord
import typing
import colors
import timedisplay
import const
import io

from discord.ext import commands
from .core import utils

SAVE_LIMIT = 10
DELETED = 'deleted'
EDITED = 'edited'

class ChannelLog:
    def __init__(self):
        self.deleted = []
        self.edited = []
    
    def get_list(self, state):
        return getattr(self, state)[-SAVE_LIMIT:]
    
    def log(self, state, message):
        msgs = self.get_list(state)
        msgs.append(message)
        setattr(self, state, msgs)
    
    def log_deleted(self, message): self.log(DELETED, message)
    def log_edited(self, message): self.log(EDITED, message)

    def get_last(self, state, index):
        try:
            return self.get_list(state)[-index]
        except:
            return None

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_logs = {}
        self.backup_files = {}
    
    @commands.command(hidden=True, aliases=['re'])
    @commands.guild_only()
    async def repeatedit(self, ctx, channel:typing.Optional[discord.TextChannel], i=1):
        channel = channel or ctx.channel
        msg = self.get_last_message(channel, EDITED, i)
        if msg:
            await ctx.send(msg.content, embed=msg.embeds[0] if msg.embeds else None)
        else:
            await ctx.send(embed=self.create_empty_embed(channel, EDITED))
    
    @commands.group(aliases=['unkolsh'])
    @commands.guild_only()
    async def snipe(self, ctx, channel:typing.Optional[discord.TextChannel], i:typing.Union[int, str]=1):
        if type(i) == str:
            await self.send_log_in_embed(ctx, channel or ctx.channel, DELETED)
            return
        elif i > 10:
            raise commands.BadArgument('You can only snipe the last 10 deleted messages!')
        await self.send_message_in_embed(ctx, channel, DELETED, i)

    @commands.command(aliases=['editsnipe'])
    @commands.guild_only()
    async def snipedit(self, ctx, channel:typing.Optional[discord.TextChannel], i=1):
        await self.send_message_in_embed(ctx, channel, EDITED, i)

    async def send_message_in_embed(self, ctx, channel, state, index):
        channel = channel or ctx.channel
        msg = self.get_last_message(channel, state, index)

        embed = self.create_empty_embed(channel, state)
        files = []
        if msg:
            await self.embed_message_log(embed, msg, state)
            files = await self.get_backup_files(msg, embed)

        await ctx.send(embed=embed, files=files)
        if msg and msg.embeds:
            await ctx.send(embed=msg.embeds[0])
    
    def get_last_message(self, channel, state, index):
        log = self.channel_logs.get(channel.id)
        msg = log.get_last(state, index) if log else None
        return msg

    def create_empty_embed(self, channel, state):
        embed = colors.embed()
        embed.description = f'No {state} messages to snipe!'
        embed.set_author(name='#' + channel.name)
        return embed
    
    async def embed_message_log(self, embed, msg, state):
        embed.set_author(name=str(msg.author), icon_url=msg.author.avatar_url)
        embed.description = msg.content or msg.system_content or ''
        embed.timestamp = msg.created_at
        embed.set_footer(text=state.capitalize())
        
        if not msg.attachments: return

        url = msg.attachments[0].proxy_url
        embed.set_image(url=url)

        links = get_attachment_links(msg, 'Link')
        embed.description += '\n' + ' '.join(links)

    async def get_backup_files(self, msg, embed):
        accessible = embed.image and await utils.download(embed.image.url, utils.READ)
        multiple_files = len(msg.attachments) > 1
        if accessible and not multiple_files: return []

        files = self.backup_files.get(msg.id, {})
        files = [discord.File(io.BytesIO(data), name) for name, data in files.items()]
        if files:
            embed.set_image(url='')
        return files
    
    @commands.command()
    @commands.guild_only()
    async def snipelog(self, ctx, channel:discord.TextChannel=None):
        await self.send_log_in_embed(ctx, channel or ctx.channel, DELETED)
    
    @commands.command()
    @commands.guild_only()
    async def editlog(self, ctx, channel:discord.TextChannel=None):
        await self.send_log_in_embed(ctx, channel or ctx.channel, EDITED)
    
    async def send_log_in_embed(self, ctx, channel, state):
        log = self.channel_logs.get(channel.id)
        embed = self.create_empty_embed(channel, state)
        self.embed_channel_logs(embed, log, state)

        await ctx.send(embed=embed)

    def embed_channel_logs(self, embed, channel_log, state):
        if not channel_log: return

        prev_msg = None
        msgs = []
        logged_msgs = channel_log.get_list(state)

        for i, m in enumerate(logged_msgs):
            extra = get_extra(m)
            time = get_time_display(m, state)

            snipe_index = min(len(logged_msgs), 10) - i
            # msg = f'**{snipe_index}:** {msg}'
            msg = f'**{snipe_index}:** `{time}` {m.content} {extra}'
            author_first_msg = not prev_msg or prev_msg.author != m.author
            if author_first_msg:
                next_msg_same_author = i + 1 < len(logged_msgs) and logged_msgs[i+1].author == m.author
                sep = '\n' if next_msg_same_author else ' '
                msg = f'{m.author.mention}{sep}{msg}'
            msgs += [msg]

            prev_msg = m
        
        if msgs:
            footer = f'{state.capitalize()}'
            embed.set_footer(text=footer)
            embed.description = '\n'.join(msgs)

    @commands.Cog.listener()
    async def on_message(self, msg):
        files = { a.filename: await a.read() for a in msg.attachments }
        if files:
            self.backup_files[msg.id] = files

    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        if not msg.guild or msg.author == self.bot.user: return
        self.get_or_create_log(msg.channel).log_deleted(msg)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild or before.author == self.bot.user: return
        self.get_or_create_log(before.channel).log_edited(before)
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, msgs):
        for m in msgs:
            self.get_or_create_log(m.channel).log_deleted(m)
    
    def get_or_create_log(self, channel):
        if channel.id not in self.channel_logs:
            self.channel_logs[channel.id] = ChannelLog()
        return self.channel_logs[channel.id]

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
