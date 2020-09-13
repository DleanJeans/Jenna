import discord
import cogs
import colors

from typing import Optional
from discord.ext import commands
from .core import converter as conv

NHOAN_COUNTER = 'nhoan_counter'
GUILD_NHOAN_SUM_COUNTER = 'guild_nhoan_sums'
NHOANMSG_FIRSTTIME = '{0} just posted nhoặn for the first time!'
NHOANMSG_UPDATE = '{0} just posted nhoặn, that\'s {1} times now!'
NHOANMSG_QUERY_0 = '{0} has not posted nhoặn. Yet!'
NHOANMSG_QUERY_N = '{0} has posted nhoặn {1} time{2}!'

NHOANEMBED_AUTHOR_N = '{0}\'s nhoặn count'
NHOANEMBED_FOOTER = 'Total server nhoặn moments counted: {0}'

TOPNHOAN_TITLE = 'Khúm núm before your nhoặn leaders!'
TOPNHOAN_ENTRY = '**{0}**: {1}, with {2} nhoặn post{3}\n'

class Nhoặn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Persist = bot.get_cog(cogs.PERSIST)
        self.allnhoan = self.Persist.get(NHOAN_COUNTER, {})
        self.allguildsnhoan = self.Persist.get(GUILD_NHOAN_SUM_COUNTER, {})

    def sync_nhoan_count(self, member: discord.Member, guild: discord.Guild, value: int):
        old_value = self.allnhoan.get(member.id, 0)
        difference = value - old_value
        
        self.allnhoan[member.id] = value
        self.Persist.set(NHOAN_COUNTER, self.allnhoan)

        self.allguildsnhoan[guild] = self.allguildsnhoan.get(guild, 0) + difference
        self.Persist.set(GUILD_NHOAN_SUM_COUNTER, self.allguildsnhoan)

    def init_embed(self, guild: discord.Guild):
        embed = colors.embed()
        embed.set_footer(text=NHOANEMBED_FOOTER.format(self.allguildsnhoan.get(guild, 0)))
        return embed

    @commands.command(aliases = ['nhoặn', 'nh'])
    async def nhoan(self, ctx, member:Optional[conv.FuzzyMember]=None):
        last_msgs = await ctx.channel.history(limit=2).flatten()
        msg_before_invoke = last_msgs[1] if len(last_msgs) > 1 else None
        if msg_before_invoke:
            member = member or msg_before_invoke.author
        else:
            await ctx.send('No last message found. I don\'t know who to add nhoặn to!')
            return

        m_id = member.id
        original_count = self.allnhoan.get(m_id, 0)
        self.sync_nhoan_count(member, ctx.guild, original_count + 1)
        
        embed = self.init_embed(ctx.guild)
        embed.set_author(name=NHOANEMBED_AUTHOR_N.format(member.name))
        if original_count == 0:
            embed.description = NHOANMSG_FIRSTTIME.format(member.name)
        else:
            embed.description = NHOANMSG_UPDATE.format(member.name, \
                str(original_count + 1))
        await ctx.send(embed = embed)

    @commands.command(aliases = ['hnh','hownh'])
    async def hownhoan(self, ctx, member:Optional[conv.FuzzyMember]=None):
        member = member or ctx.author
        m_id = member.id
        nhoantimes = self.allnhoan.get(m_id, 0)
        embed = self.init_embed(ctx.guild)
        embed.set_author(name=NHOANEMBED_AUTHOR_N.format(member.name))
        if nhoantimes == 0:
            embed.description = NHOANMSG_QUERY_0.format(member.name)
        else:
            embed.description = NHOANMSG_QUERY_N.format(member.name, \
                str(nhoantimes), 's' if nhoantimes != 1 else '')
        await ctx.send(embed = embed)

    @commands.command(aliases = ['tnh', 'topnh'])
    async def topnhoan(self, ctx):
        allnhoan = self.allnhoan
        msg = ''
        allnhoan_processed = filter(lambda tup: tup[0] is not None,
            zip(map(lambda m_id: self.bot.get_user(int(m_id)), allnhoan),
                allnhoan.values()))
        top5 = sorted(allnhoan_processed, key = lambda tup: tup[1], reverse = True)[:5]
        for i, (memb, nhoantimes) in enumerate(top5):
            msg+= TOPNHOAN_ENTRY.format(
                i+1, memb.name, nhoantimes, 's' if nhoantimes != 1 else '')
        embed = self.init_embed(ctx.guild)
        embed.set_author(name = TOPNHOAN_TITLE)
        embed.description = msg
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Nhoặn(bot))
