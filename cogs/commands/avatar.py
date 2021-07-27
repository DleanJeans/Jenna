import discord
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from cogs.common import colors
from datetime import datetime


async def avatar(ctx: SlashContext, user: discord.User = None):
    member = user or ctx.author
    embed = colors.embed(description=member.mention)
    embed.title = str(member)
    embed.set_image(url=str(member.avatar_url).replace('webp', 'png'))
    embed.timestamp = datetime.now().astimezone()
    await ctx.send(embed=embed)


run = avatar
props = {
    'description':
    "Zoom in on someone's avatar before they yeet it or show everyone how awesome your avatar is!"
}
