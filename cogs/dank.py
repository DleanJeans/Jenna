import discord
import re
import const
import env

from discord.ext import commands
from .core.dank.unscramble import unscramble

DANK_MEMER = 'Dank Memer'

RETYPE = 'Type'
TYPING = 'typing'
COLOR = 'Color'
MEMORY = 'Memory'
REVERSE = 'Reverse'
SCRAMBLE = 'scramble'
EMOJI_MATCH = 'Emoji Match'
GAMES_TO_HELP = [EMOJI_MATCH, RETYPE, COLOR, MEMORY, REVERSE, TYPING, SCRAMBLE]

WORD_PATTERN = '`(.+?)`'
COLOR_WORD_PATTERN = ':(\w+):.* `([\w-]+)`'
INVISIBLE_TRAP = '﻿'
COLOR_WORD_FORMAT = ':{color}_square: `{word}` = `{color}`'

EVENT_ENCOUNTERED = 'EVENT TIME'
UNSCRAMBLE_ERROR = ':warning: Could not unscramble word'

GAMBLING_ADDICT = 'Gambling Addict'
RETADABAR_ID = 614712933997346817

class DankHelper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if env.TESTING: return
        not_dank_memer_or_self = msg.author.name not in [DANK_MEMER, self.bot.user.name]
        in_dm = isinstance(msg.channel, discord.DMChannel)
        if not_dank_memer_or_self or in_dm: return

        is_minigame = any(word in msg.content for word in GAMES_TO_HELP)
        is_event = EVENT_ENCOUNTERED in msg.content

        help = None
        if is_minigame:
            help = self.send_minigame_assist
        elif is_event:
            help = self.ping_players

        if help:
            await help(msg)

    async def ping_players(self, msg):
        if msg.guild.id != RETADABAR_ID: return
        player_role = discord.utils.get(msg.guild.roles, name=GAMBLING_ADDICT)
        await msg.channel.send(f'{player_role.mention} This is a **NOT** test!')
    
    async def send_minigame_assist(self, msg):
        content = msg.content.replace(INVISIBLE_TRAP, '')
        words_in_backticks = re.findall(WORD_PATTERN, content)
        backticked_word = words_in_backticks[0] if len(words_in_backticks) == 1 else ''
        
        if COLOR in msg.content:
            lines = []
            color_word_pairs = re.findall(COLOR_WORD_PATTERN, content)
            for color, word in color_word_pairs:
                lines += [COLOR_WORD_FORMAT.format(color=color, word=word)]
            content = '\n'.join(lines)
        elif REVERSE in msg.content:
            content = backticked_word[::-1]
        elif SCRAMBLE in msg.content.lower():
            anagrams = [await unscramble(word) for word in words_in_backticks]
            content = '\n'.join(' '.join(a) for a in anagrams)
        elif any(word in msg.content for word in [RETYPE, TYPING]):
            content = backticked_word
        elif MEMORY in msg.content:
            content = content.split('`')[1].replace('\n', ' ')
        elif EMOJI_MATCH in msg.content:
            content = msg.content.splitlines()[1]
        else:
            return
        
        if content:
            await msg.channel.send(content)

def setup(bot):
    bot.add_cog(DankHelper(bot))
