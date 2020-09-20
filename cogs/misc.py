import discord
import colors
import const
import timedisplay
import time

from typing import Optional
from discord.ext import commands, tasks
from datetime import datetime
from .core import converter as conv
from .core.misc import covid, math, reddit
from urllib.parse import quote_plus

MATH_BRIEF = 'Compute big numbers for you'
INVITE_LINK = 'https://discordapp.com/api/oauth2/authorize?client_id=664109951781830666&permissions=1342565440&scope=bot'

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.corona_status = covid.CoronaStatus()

    @commands.command(aliases=['gg', 'g', 'whats'])
    async def google(self, context, *, query=None):
        if not query:
            last_message = await context.history(limit=1, before=context.message).flatten()
            query = last_message[0].clean_content or ''
        query = ''.join(char if char.isalpha() else quote_plus(char) for char in query)
        url = 'https://www.google.com/search?q=' + query
        await context.send(url)

    @commands.command(hidden=True)
    async def do(self, context, subcommand, *, line=None):
        if subcommand not in ['math', 'meth']:
            line = subcommand + line
        await math.compute(context, line)

    @commands.command(aliases=['meth'])
    async def math(self, context, *, line):
        await math.compute(context, line)

    @commands.command()
    @commands.guild_only()
    async def whos(self, context, *, member:Optional[conv.FuzzyMember]=None):
        member = member or context.author
        
        response = f'It\'s **{member}**'
        embed = colors.embed()
        embed.description = member.mention
        created_at = timedisplay.to_ict(member.created_at, timedisplay.DAYWEEK_DAY_IN_YEAR)
        joined_at = timedisplay.to_ict(member.joined_at, timedisplay.DAYWEEK_DAY_IN_YEAR)
        embed \
            .set_thumbnail(url=member.avatar_url) \
            .add_field(name='On Discord since', value=created_at, inline=False) \
            .add_field(name='Joined on', value=joined_at)

        await context.send(response, embed=embed)
    
    @commands.command()
    async def invite(self, context):
        worryluv = discord.utils.get(self.bot.emojis, name='worryluv')
        embed = colors.embed()
        embed.description = f'{worryluv} [Click here]({INVITE_LINK}) to invite {self.bot.user.name}!'
        await context.send(embed=embed)
    
    @commands.command(aliases=['cv', 'ncov', 'corona', 'morning'])
    async def covid(self, context, *, region='server'):
        await context.trigger_typing()
        empty = covid.create_empty_embed()
        msg = await context.send(embed=empty)

        await self.corona_status.update()
        data = self.corona_status.data

        emotes = ['khabanhquay']
        emotes = [str(discord.utils.get(self.bot.emojis, name=e)) for e in emotes]
        covid.set_emotes(*emotes)

        try:
            embed = covid.embed_countries(data) if region == 'server' \
                else covid.embed_region(data, region)
        except commands.UserInputError as e:
            embed = empty
            embed.description = e.args[0]
        embed.color = empty.color
        await msg.edit(embed=embed)
    
    @commands.group(name='reddit', aliases=['r', 'rd'], invoke_without_command=True)
    async def _reddit(self, context, sub='random', sorting:Optional[reddit.sorting]='top', \
        posts:Optional[reddit.posts]=1, *, top:reddit.period='today'):
        await context.trigger_typing()
        try:
            sub = reddit.subname(sub)
        except reddit.RedditError:
            sorting = reddit.sorting(sub)
            sub = 'random'
        await reddit.send_posts_in_embeds(context, sub, sorting, posts, top)

    @_reddit.command(aliases=['t'], hidden=True)
    async def top(self, context, sub:Optional[reddit.subname]='random', posts:reddit.posts='1'):
        await context.trigger_typing()
        await reddit.send_posts_in_embeds(context, sub, 'top', posts)

def setup(bot):
    bot.add_cog(Misc(bot))
