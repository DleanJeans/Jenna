import discord
import cogs
import colors

from typing import Optional, Union
from discord.ext import commands
from .core import converter as conv

TITLE = 'Nhoặn Counter'

NHOAN_COUNTER = 'nhoan_counter'
GUILD_NHOAN_SUM_COUNTER = 'guild_nhoan_sums'

NHOANMSG_FIRSTTIME = '{0} just posted nhoặn for the first time!'
NHOANMSG_UPDATE = '{0} just posted nhoặn, that\'s {1} times now!'
NHOANMSG_QUERY_0 = '{0} has not posted nhoặn. Yet!'
NHOANMSG_QUERY_N = '{0} has posted nhoặn {1} time{2}, ranking **{3}** in the server!'

NHOANEMBED_FOOTER = 'Total server nhoặn moments counted: {0}'

TOPNHOAN_TITLE = 'Khúm núm before your nhoặn leaders!'
TOPNHOAN_ENTRY = '**{0}**: {1}, with {2} nhoặn post{3}\n'

NHOAN_SYNONYMS = ['nhoan', 'nhoặn', 'cringe', 'crimge']

class Nhoan(commands.Cog, name='Nhoặn'):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.Persist = self.bot.get_cog(cogs.PERSIST)
        await self.Persist.wait_until_loaded()
        self.allnhoan = self.Persist.get(NHOAN_COUNTER, {})
        self.allguildsnhoan = self.Persist.get(GUILD_NHOAN_SUM_COUNTER, {})
        
        self.Persist.set(NHOAN_COUNTER, self.allnhoan)
        self.Persist.set(GUILD_NHOAN_SUM_COUNTER, self.allguildsnhoan)

    def sync_nhoan_count(self, member: discord.Member, guild: discord.Guild, value: int):
        old_value = self.allnhoan.get(member.id, 0)
        difference = value - old_value
        
        self.allnhoan[member.id] = value
        self.allguildsnhoan[guild] = self.allguildsnhoan.get(guild, 0) + difference

    def init_embed(self, guild: discord.Guild):
        embed = colors.embed(title=TITLE)
        embed.set_footer(text = NHOANEMBED_FOOTER.format(self.allguildsnhoan.get(guild, 0)))
        return embed
    
    def get_sorted_counts(self, guild: discord.Guild, count = 0):
        allnhoan = self.allnhoan
        allnhoan_top = sorted(filter(lambda tup: tup[0] is not None, 
            zip(map(lambda m_id: guild.get_member(int(m_id)), allnhoan), allnhoan.values())), 
            key = lambda tup: tup[1], reverse = True)
        if count > 0:
            return enumerate(allnhoan_top[:count], start = 1)
        else:
            return enumerate(allnhoan_top, start = 1)
        
    @commands.Cog.listener()
    async def on_message(self, msg):
        ctx = await self.bot.get_context(msg)
        if ctx.command: return
        content = msg.content
        content = content.replace(ctx.prefix, '', 1) if ctx.prefix and content.startswith(ctx.prefix) else content

        for nhoan in NHOAN_SYNONYMS:
            if nhoan in content.split():
                possible_name = content.split(nhoan)[0]
                try:
                    member = await conv.members.FuzzyMemberConverter(matching=.7).convert(ctx, possible_name)
                    await self.bump_nhoan_count(ctx, member)
                except:
                    pass
                return
    
    @commands.command(aliases = ['nhoặn', 'nh', 'cringe', 'crimge'])
    async def nhoan(self, ctx, member: Optional[conv.FuzzyMember] = None):
        last_msgs = await ctx.channel.history(limit=5).flatten()
        msg_before_invoke = last_msgs[1] if len(last_msgs) > 1 else None
        if msg_before_invoke:
            member = member or msg_before_invoke.author
        else:
            await ctx.send('No last message found. I don\'t know who to add nhoặn to!')
            return

        await self.bump_nhoan_count(ctx, member)

    async def bump_nhoan_count(self, ctx, member):
        if member == ctx.message.author:
            await ctx.send('You cannot call nhoặn on yourself!')
            return
        
        original_count = self.allnhoan.get(member.id, 0)
        self.sync_nhoan_count(member, ctx.guild, original_count + 1)
        
        embed = self.init_embed(ctx.guild)
        name = f'**{member.display_name}**'
        mention = f' {member.mention}'
        if original_count == 0:
            embed.description = NHOANMSG_FIRSTTIME.format(name) + mention
        else:
            embed.description = NHOANMSG_UPDATE.format(name, \
                str(original_count + 1)) + mention
        await ctx.send(embed = embed)

    @commands.command()
    async def denhoan(self, ctx, member:Optional[conv.FuzzyMember], count=1):
        original_count = self.allnhoan.get(member.id, 0)
        new_count = original_count - count
        self.sync_nhoan_count(member, ctx.guild, max(0, new_count))
        embed = self.init_embed(ctx.guild)
        embed.description = f'Nhoặn count for **{member.display_name}** changed to: {new_count}'
        await ctx.send(embed = embed)

    @commands.command(aliases = ['hownh', 'nhoancount', 'cringecount', 'crimgecount'])
    async def hownhoan(self, ctx, member: Optional[conv.FuzzyMember] = None):
        member = member or ctx.author
        times = 0
        
        for rank, (mem, nhoantimes) in self.get_sorted_counts(ctx.guild):
            if mem == member:
                times = nhoantimes
                break
        
        embed = self.init_embed(ctx.guild)
        if times == 0:
            you = 'You ' if member == ctx.author else ''
            embed.description = you + NHOANMSG_QUERY_0.format(member.mention)
        else:
            # get_ordinal implementation from https://stackoverflow.com/a/36977549
            get_ordinal = lambda n: \
                "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}.get(n if n < 20 else n % 10, "th"))
            embed.description = NHOANMSG_QUERY_N.format(member.mention, \
                str(times), 's' if times != 1 else '', get_ordinal(rank))
        await ctx.send(embed = embed)

    @commands.command(aliases = ['topnh', 'nhoankings', 'topcringe', 'topcrimge'])
    async def topnhoan(self, ctx, count: Optional[int] = 5):
        msg = ''
        for i, (member, nhoantimes) in self.get_sorted_counts(ctx.guild, count):
            msg += TOPNHOAN_ENTRY.format(
                i, member.mention, nhoantimes, 's' if nhoantimes != 1 else '')
        embed = self.init_embed(ctx.guild)

        embed.title = TOPNHOAN_TITLE
        embed.description = msg
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Nhoan(bot))
