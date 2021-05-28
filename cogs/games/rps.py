import discord
import random
import time

from operator import attrgetter

ROCK = '✊'
PAPER = '🖐️'
SCISSORS = '✌️'
RPS_EMOTES = [ROCK, PAPER, SCISSORS]

TO_RPS = 'to a match of **Rock Paper Scissors!**'
CHOOSE = ' Choose a hand below:'

def get_winning_hand(hands):
    h1, h2 = hands
    if h1 == h2: return None
    indices = list(map(RPS_EMOTES.index, (h1, h2)))
    indices.sort()
    if indices == [0, 2]:
        return ROCK
    return RPS_EMOTES[max(indices)]

class RPSGame:
    def __init__(self, bot, players, sets, rounds):
        self.bot = bot
        self.players = players
        self.sets = max(1, sets)
        self.rounds = max(1, rounds)
        self.set = 1
        self.round = 1
        self.rounds_won = [0] * 2
        self.sets_won = [0] * 2
        self.winner = None
        self.loser = None
        self.set_winner = None
        self.last_set = []
        self.rounds_history = []
    
    def is_single(self):
        return self.sets == self.rounds == 1
    
    def add_round(self, hands):
        self.current = RPSRound(self.players, hands)
        return self.current
    
    def move_on(self):
        self.round += 1
        self.set_winner = None
        self.set_loser = None
        self.rounds_history += [self.rounds_won]
        if self.current.is_draw(): return

        windex = self.current.windex
        self.rounds_won[windex] += 1

        if self.rounds_won[windex] >= self.rounds:
            self.sets_won[windex] += 1
            self.set_winner = self.current.winner
            self.set_loser = self.players[1-windex]
            self.set += 1
            self.round = 1
            self.last_set = self.rounds_won
            self.rounds_won = [0] * 2

            if self.sets_won[windex] >= self.sets:
                self.winner = self.set_winner
                self.loser = self.set_loser
                

class RPSRound:
    def __init__(self, players, hands):
        self.players = players
        self.hands = hands
        self.winning_hand = get_winning_hand(self.hands)
        self.windex = self._get_windex()
        self.winner = self._get_winner()
    
    def is_draw(self):
        return not self.winning_hand
    
    def _get_windex(self):
        if self.winning_hand:
            return self.hands.index(self.winning_hand)

    def _get_winner(self):
        if self.winning_hand:
            return self.players[self.windex]

class RPSAnnouncer:
    def __init__(self, game):
        self.game = game
        self.wait_msg = None
        self.hands = []
    
    def get_full_round_name(self):
        names = [self.get_set_name(), self.get_round_name()]
        return ''.join(names)

    def get_round_name(self):
        if self.game.rounds > 1:
            return f'**Round {self.game.round}**'
        return ''
    
    def get_set_name(self):
        if self.game.sets > 1 and self.game.round == 1:
            return f'**Set {self.game.set}**\n'
        return ''
    
    def get_round_result(self, with_name=True):
        hands = self.game.current.hands
        names = self.get_names() if with_name else [''] * 2
        round_scores = ' - '.join(map(str, self.game.rounds_history[-1]))
        if self.game.current.is_draw():
            round_scores = '**DRAW**'

        result = f'{names[0]} {hands[0]} {round_scores} {hands[1]} {names[1]}'
        return result.strip()

    def for_player(self, msg, player):
        return msg.replace(player.display_name, 'You')

    def get_draw_msg(self):
        return f"It's a {self.game.current.hands[0]} **DRAW**!"
    
    def get_end_result(self, player=None):
        name = f'__{self.game.winner.display_name}__' if player else self.game.winner.mention
        return f'{name} won the game!'
    
    def get_names(self):
        names = [f'__{p.display_name}__' for p in self.game.players]
        return names

    def get_set_result(self):
        winner_name = self.game.set_winner.display_name
        total_scores = ' - '.join(map(str, self.game.sets_won))
        return f'__{winner_name}__ won **Set {self.game.set - 1}** ({total_scores})'

    async def send_wait_msg(self, player, for_player):
        self.wait_msg = await player.send(f'Waiting for **{for_player.display_name}**...')

    async def delete_wait_msg(self):
        if self.wait_msg:
            await self.wait_msg.delete()
            self.wait_msg = None
    
    async def send_challenge(self, i):
        friend_name = get_full_name(self.game.players[1-i]).replace(str(self.game.bot.user), 'me')
        msg = f'{friend_name} challenged you {TO_RPS}' if i \
        else f'You challenged {friend_name} {TO_RPS}'
        await self.game.players[i].send(msg)

    async def send_dms_for_hands(self):
        full_round_name = self.get_full_round_name()
        round_num = len(self.game.rounds_history) + 1
        players_reversed = round_num % 2 == 0
        players = self.game.players[::]
        if players_reversed:
            players.reverse()

        hands = []
        msgs = []

        for i, p in enumerate(players):
            if p.bot:
                random.seed(time.time())
                hand = random.choice(RPS_EMOTES)
                hands += [hand]
                msgs += [None]
                continue

            if round_num == 1:
                await self.send_challenge(i)

            msg = await p.send(full_round_name)
            msgs += [msg]

            for emote in RPS_EMOTES:
                await msg.add_reaction(emote)

            msg = await p.fetch_message(msg.id)
            quick_reaction = max(msg.reactions, key=attrgetter('count'))
            if quick_reaction.count >= 2:
                reaction = quick_reaction
            else:
                def check(reaction, user):
                    return reaction.message.id == msg.id and user == p and reaction.emoji in RPS_EMOTES
                reaction, _ = await self.game.bot.wait_for('reaction_add', check=check)

            hand = reaction.emoji
            hands += [hand]
            await msg.edit(content=f'{full_round_name} You threw {hand}')

            if i == 0 and not players[1].bot:
                await self.delete_wait_msg()
                await self.send_wait_msg(p, players[1])
                
        if players_reversed:
            hands.reverse()
            msgs.reverse()
        return hands, msgs

def get_full_name(member):
    name = f'{member}'
    if member.display_name != member.name:
        name = f'{member.display_name} ({name})'
    return f'**{name}**'