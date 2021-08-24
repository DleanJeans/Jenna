import discord
from cogs.common import colors
from datetime import datetime


async def avatar(ctx, user: discord.User = None):
    embed = run_embed(ctx, user)
    await ctx.send(embed=embed)


def run_embed(ctx, user):
    member = user or ctx.author
    embed = colors.embed(description=member.mention)
    embed.title = str(member)
    embed.set_image(url=str(member.avatar_url))
    embed.timestamp = datetime.now().astimezone()
    return embed


async def send_with_announcement(ctx, user):
    embed = run_embed(ctx, user)
    ANNOUNCEMENT = '`/avatar` slash command is available!'
    await ctx.send(ANNOUNCEMENT, embed=embed)


send = avatar
props = {
    'description':
    "Zoom in on someone's avatar before they yeet it or show everyone how awesome your avatar is!"
}
