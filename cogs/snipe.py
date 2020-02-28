import discord
import colors

from datetime import timezone
from discord.ext import commands

DELETED = 'deleted'
EDITED = 'edited'

class ChannelMessageLog:
    def __init__(self):
        self.deleted = []
        self.edited = []
    
    def get_list(self, state):
        return getattr(self, state)
    
    def log(self, state, message):
        self.get_list(state).append(message)
    
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

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = {}
    
    @commands.group(hidden=True)
    @commands.guild_only()
    async def snipe(self, context, index=None, subindex=None):
        if index == 'edit':
            await self.edit(context, subindex)
            return
        elif index == 'editlog':
            await self.send_edit_log(context, subindex)
            return

        if index and not str(index).isdigit():
            return
        
        await self.send_message_in_embed(context, DELETED, index)
    
    async def edit(self, context, index=1):
        await self.send_message_in_embed(context, EDITED, index)

    async def send_message_in_embed(self, context, state, index):
        if not index:
            index = 1
        elif type(index) is str:
            index = int(index)

        guild = self.guilds.get(context.guild.id)
        msg = guild.get_last(context.channel, state, index) if guild else None

        embed = self.create_empty_embed(context.channel, state)
        self.embed_message_log(embed, msg, state)

        if msg and msg.embeds:
            await context.send(embed=msg.embeds[0])
        await context.send(embed=embed)

    def create_empty_embed(self, channel, state):
        embed = discord.Embed(color=colors.random())
        embed.description = f'No {state} messages to snipe!'
        embed.set_author(name='#' + channel.name)
        return embed
    
    def embed_message_log(self, embed, msg, state):
        if msg:
            full_name = f'{msg.author.name}#{msg.author.discriminator}'
            embed.set_author(name=full_name, icon_url=msg.author.avatar_url)
            embed.description = msg.content or None
            embed.timestamp = msg.created_at
            embed.set_footer(text=state.capitalize())
            
            if msg.attachments:
                embed.set_image(url=msg.attachments[0].proxy_url)
    
    @commands.command(hidden=True)
    @commands.guild_only()
    async def snipelog(self, context, channel:discord.TextChannel=None):
        await self.send_log_in_embed(context, channel, DELETED)
    
    @commands.command(hidden=True)
    @commands.guild_only()
    async def editlog(self, context, channel:discord.TextChannel=None):
        await self.send_edit_log(context, channel)
    
    async def send_edit_log(self, context, channel):
        await self.send_log_in_embed(context, channel, EDITED)

    async def send_log_in_embed(self, context, channel, state):
        if not channel:
            channel = context.channel
        
        guild_log = self.guilds.get(context.guild.id)
        channel_log = guild_log.channels.get(channel.id) if guild_log else None

        embed = self.create_empty_embed(channel, state)
        self.embed_channel_logs(embed, channel_log, state)

        await context.send(embed=embed)

    def embed_channel_logs(self, embed, channel_log, state):
        if channel_log:
            snipes = []
            for m in channel_log.get_list(state):
                extra = ''
                if m.attachments:
                    extra = f'[[Attachment]]({m.attachments[0].proxy_url})'
                elif m.embeds:
                    extra = '[Embed]'

                time = m.created_at.replace(tzinfo=timezone.utc).astimezone().strftime('%H:%M')
                snipes += [f'*{time}* {m.author.mention} {m.content} {extra}']
            
            if snipes:
                embed.description = '\n'.join(snipes)
                embed.set_footer(text=state.capitalize())

    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        guild = msg.channel.guild
        guild = self.get_guild_log(msg.channel.guild)
        guild.log_deleted(msg)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content == after.content: return

        guild = self.get_guild_log(after.channel.guild)
        guild.log_edited(before)
    
    def get_guild_log(self, guild):
        if guild.id not in self.guilds:
            self.guilds[guild.id] = GuildMessageLog()
        return self.guilds[guild.id]

def setup(bot):
    bot.add_cog(Snipe(bot))