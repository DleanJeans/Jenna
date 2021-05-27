import discord
import re
import const

from discord.ext import commands
from operator import attrgetter
from .core import converter as conv
from .core.games.rps import RPS_EMOTES, RPSGame, RPSAnnouncer

TO_RPS = 'to a match of **Rock Paper Scissors!**'
CHOOSE = ' Choose a hand below:'

def get_name(member):
    name = f'{member}'
    if member.display_name != member.name:
        name = f'{member.display_name} ({name})'
    return f'**{name}**'


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = []
    
    @commands.command()
    @commands.guild_only()
    async def rps(self, ctx, friend:conv.FuzzyMember, rounds:int=2, sets:int=1):
        cannot_play = ''
        if ctx.author == friend:
            cannot_play = 'You can\'t play with yourself ya know.'
        elif any(friend in game.players for game in self.games):
            cannot_play = f'**{friend.display_name}** is in the middle of another game. Ask them later!'
        elif any(ctx.author in game.players for game in self.games):
            cannot_play = f'Finish your ongoing game first!'
        
        if cannot_play:
            await ctx.send(cannot_play)
            return
        
        rounds = max(1, rounds)
        ets = max(1, sets)

        players = [ctx.author, friend]
        game = RPSGame(self.bot, players, sets, rounds)
        announcer = RPSAnnouncer(game)
        self.games += [game]

        summary = [f'{players[0].mention} vs {players[1].mention}']
        total_round = 0
        wait_msg = None
        while True:
            total_round += 1
            round_name = announcer.get_full_round_name()
            set_name = announcer.get_set_name()
            
            hands, msgs = await announcer.send_dms_for_hands()
            current_round = game.add_round(hands)
            
            game.move_on()

            summary += [set_name + announcer.get_round_result(with_name=False)]
            round_result = set_name + announcer.get_round_result()
            for p, m in zip(players, msgs):
                if m:
                    await m.edit(content=announcer.for_player(round_result, p))
            
            if sets > 1 and game.set_winner:
                set_result = announcer.get_set_result()
                summary += [set_result]
                for p in players:
                    if not p.bot:
                        await p.send(announcer.for_player(set_result, p))
            if game.winner:
                break
        
        if not game.is_single():
            end_result = announcer.get_end_result()
            summary += [end_result]
            for p in players:
                if p.bot: continue
                end_result = announcer.get_end_result(p)
                end_result = announcer.for_player(end_result, p)
                await p.send(end_result)
        
        summary = '\n'.join(summary)
        await ctx.send(summary)

        self.games.remove(game)
    
def setup(bot):
    bot.add_cog(Games(bot))