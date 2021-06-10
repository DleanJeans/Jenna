import discord

from . import covid, math, reddit
from ..common import colors
from ..common import converter as conv
from ..common import timedisplay
from ..common import utils
from discord.ext import commands
from urllib.parse import quote_plus
from typing import Optional


MATH_BRIEF = 'Compute big numbers for you'
INVITE_LINK = 'https://discord.com/api/oauth2/authorize?client_id=664109951781830666&permissions=3758484544&scope=bot'

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.corona_status = covid.CoronaStatus()

    @commands.command(aliases=['gg', 'g', 'whats'])
    async def google(self, ctx, *, query=None):
        if not query:
            last_message = await ctx.history(limit=1, before=ctx.message).flatten()
            query = last_message[0].clean_content or ''
        query = ''.join(char if char.isalpha() else quote_plus(char) for char in query)
        url = 'https://www.google.com/search?q=' + query
        await ctx.send(url)

    @commands.command(aliases=['meth'])
    async def math(self, ctx, *, line):
        await math.compute(ctx, line)

    @commands.command(aliases=["who's", 'whois'])
    @commands.guild_only()
    async def whos(self, ctx, *, member:Optional[conv.FuzzyMember]=None):
        member = member or ctx.author
        
        response = f'It\'s **{member}**'
        embed = colors.embed()
        embed.description = member.mention
        created_at = timedisplay.to_ict(member.created_at, timedisplay.DAYWEEK_DAY_IN_YEAR)
        joined_at = timedisplay.to_ict(member.joined_at, timedisplay.DAYWEEK_DAY_IN_YEAR)
        embed \
            .set_thumbnail(url=member.avatar_url) \
            .add_field(name='On Discord since', value=created_at, inline=False) \
            .add_field(name='Joined on', value=joined_at)

        await ctx.send(response, embed=embed)
    
    @commands.command()
    async def invite(self, ctx):
        worryluv = discord.utils.get(self.bot.emojis, name='worryluv')
        embed = colors.embed()
        embed.description = f'{worryluv} [Click here]({INVITE_LINK}) to invite {self.bot.user.name}!'
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['cv', 'ncov', 'corona', 'morning'])
    async def covid(self, ctx, *, region='server'):
        await ctx.trigger_typing()
        empty = covid.create_empty_embed()
        msg = await ctx.send(embed=empty)

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
    async def _reddit(self, ctx, sub='random', sorting:Optional[reddit.sorting]='top', \
        posts:Optional[reddit.posts]=1, *, top:reddit.period='today'):
        await ctx.trigger_typing()
        try:
            sub = reddit.subname(sub)
        except reddit.RedditError:
            sorting = reddit.sorting(sub)
            sub = 'random'
        await reddit.send_posts_in_embeds(ctx, sub, sorting, posts, top)

    @_reddit.command(aliases=['t'], hidden=True)
    async def top(self, ctx, sub:Optional[reddit.subname]='random', posts:reddit.posts='1'):
        await ctx.trigger_typing()
        await reddit.send_posts_in_embeds(ctx, sub, 'top', posts)
    
    @commands.Cog.listener()
    async def on_message(self, msg):
        ctx = await self.bot.get_context(msg)
        if await utils.is_user_on_local(ctx):
            return
        msg = await reddit.detect_post_url_to_send_media_url(ctx)
        if not msg:
            return

        React = self.bot.get_cog('React')
        if not React:
            return

        async def resend_msg(r, u):
            await msg.edit(content=msg.content)
        if not msg.embeds:
            await React.add_button(msg, '🔁', resend_msg, delete_after=60)


def setup(bot):
    bot.add_cog(Misc(bot))