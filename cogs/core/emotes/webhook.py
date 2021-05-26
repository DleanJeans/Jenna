import discord
import re

from .const import *

WEBHOOK_FEATURE_ALERT = ('**New Feature Alert**: '
'Requires `Manage Webhooks` permission to send emotes under your name. '
'You can still use `{}say :emote:` to send emotes under my name.')

async def get_webhook(ctx):
    channel_webhooks = await ctx.channel.webhooks()
    webhook = discord.utils.get(channel_webhooks, user=ctx.me)
    if not webhook:
        webhook = await ctx.channel.create_webhook(name=ctx.me.name)
    return webhook

def initialize_guild_blacklist(self):
    try:
        self.guild_blacklist
    except AttributeError:
        self.guild_blacklist = []

async def try_send(self, ctx, emojis):
    if type(ctx.channel) is discord.DMChannel:
        await ctx.send(emojis)
        return

    send_as_self = False
    ask_for_manage_webhooks = False
    
    author = ctx.author
    perms = ctx.channel.permissions_for(ctx.me)
    initialize_guild_blacklist(self)

    if not perms.manage_webhooks:
        send_as_self = True
        ask_for_manage_webhooks = True
    else:            
        if ctx.guild in self.guild_blacklist:
            send_as_self = True
        else:
            webhook = await get_webhook(ctx)
            webhook_msg = await webhook.send(emojis, username=author.display_name, avatar_url=author.avatar_url, wait=True)

            real_emotes = re.findall(REAL_EMOJI_PATTERN, webhook_msg.content)
            if not real_emotes:
                await webhook_msg.delete()
                self.guild_blacklist.append(ctx.guild)
                send_as_self = True
    
    if send_as_self:
        await ctx.send(emojis)
    
    msg_emoji_free = re.sub(EMOJI_PATTERN, '', ctx.message.content).strip()
    if msg_emoji_free == '':
        await self.React.add_delete_button(ctx.message, author)
    
    if ask_for_manage_webhooks:
        alert_msg = await ctx.send(WEBHOOK_FEATURE_ALERT.format(ctx.bot.command_prefix[0]))
        await self.React.add_delete_button(alert_msg)