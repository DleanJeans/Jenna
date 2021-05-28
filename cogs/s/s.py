import random
import time

from . import lsqc, lstv, tarot
from ..common import converter as conv
from ..common import colors
from discord.ext import commands

def BirthTime(hour):
    try:
        hour = int(hour)
        if hour == 24:
            hour = 0
    except:
        hour = -1
    if not 0 <= hour <= 24:
        raise commands.BadArgument('`BirthTime` must be in 24-hour format')
    return hour

def get_lifepath(dob):
    lifepath = sum(dob.numbers) % 9
    if lifepath == 0:
        lifepath = 9
    return lifepath

class S(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(hidden=True)
    async def life(self, ctx):
        pass
    
    @life.command()
    async def path(self, ctx, dob:conv.DOB):
        await self.send_lifepath(ctx, dob)

    @commands.command(hidden=True)
    async def lifepath(self, ctx, dob:conv.DOB):
        await self.send_lifepath(ctx, dob)

    async def send_lifepath(self, ctx, dob):
        lifepath = get_lifepath(dob)
        await ctx.send(f'The Life Path for **{dob}** is **Number {lifepath}**')
    
    @commands.command(aliases=['lstv'])
    async def lasotuvi(self, ctx, dob:conv.DOB, birthtime:BirthTime, gender:conv.Gender, *, name=None):
        image_url = lstv.compile_url(dob, birthtime, gender, name)
        gender = conv.get_gender_emote(gender)
        embed = colors.embed(title=f'{gender} {dob} {birthtime}h', url=image_url)
        embed.set_image(url=image_url)

        await ctx.send(embed=embed)
    
    @commands.command(aliases=['lsqc'])
    async def lasoquycoc(self, ctx, dob:conv.DOB, birthtime:BirthTime):
        await ctx.trigger_typing()
        qc = await lsqc.lookup(dob, birthtime)
        text = qc.format_laso()

        embed = colors.embed(title=f'Lá số Quỷ Cốc {dob} {birthtime}h')
        embed.url = lsqc.compile_url(dob, birthtime)
        qc.add_details_as_field(embed)
        await ctx.send(text, embed=embed)
    
    @commands.command()
    async def tarot(self, ctx):
        seed = f'{ctx.author.name}#{ctx.author.discriminator}@{time.time()}'
        random.seed(seed)
        cards = tarot.CARDS[::]
        card = random.choice(cards)
        name, image, url = card
        embed = colors.embed(title=name, url=url)
        embed.set_image(url=image)
        embed.set_footer(text='Tip: Click the title to see the meaning!')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(S(bot))