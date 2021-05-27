import discord
import time
import random
import env

from discord.ext import commands

NEUTRAL_EMOJIS = [
    'worry',
    'worrysmart',
    'worryhong',
    'timmi',
    'ti',
    'worrythonk',
    'thonk',
    'nani',
    'muoi',
    'hung',
    'me',
    'hype',
    'comfychair',
]

PEEKS = [
    'peek',
    'peekmorning',
    'peekpopcorn',
]

LUV_EMOJIS = [
    'worryluv',
    'peekluv',
    'hehe',
    'fite',
    'pepeaww',
    'morning',
    'morningspoon',
    'heartpika',
    'emoji_34',
]
MAD_EMOJIS = [
    'worryduoi',
    'worrygun',
    'worrycri',
    'worrycomeatme',
    'torch',
    'sad',
    'imfine',
    'vayluon',
    'trandan',
    'sorry',
    'suspicioustom',
    'sad',
    'hmmm',
    'buonvl',
    'autism',
    'buttface',
    'feelsbadbruh',
    'furious_wojak',
    'kms~1',
    'pepepunch',
    'pain',
    'sad_cat_shoot',
    'feelspepospin',
]

LOVE_WORDS = ['luv', 'love', 'iu', 'thank', 'good', 'yeu', 'yêu', 'great', 'gr8', 'useful']
HATE_WORDS = ['fuck', 'screw', 'hate', 'ghet', 'ngu', 'ritord', 'retard', 'bad', 'crap', 'stupid']

PEEK_COOLDOWN = 10 * 60

class Cute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_mention = 0
     
    @commands.Cog.listener()
    async def on_message(self, msg):
        if env.TESTING or msg.author == self.bot.user: return
        ctx = await self.bot.get_context(msg)
        if ctx.command:
            return
        if self.mentioned_in(msg):
            await self.drop_emojis(msg)
    
    async def drop_emojis(self, msg):
        if contains_words(msg, LOVE_WORDS):
            emoji = random.choice(LUV_EMOJIS)
        elif contains_words(msg, HATE_WORDS):
            emoji = random.choice(MAD_EMOJIS)
        elif contains_words(msg, ['weed']):
            emoji = 'bigeyes'
        else:
            last_mention_ago = time.time() - self.last_mention
            gotta_peek = last_mention_ago > PEEK_COOLDOWN
            emoji = random.choice(PEEKS if gotta_peek else NEUTRAL_EMOJIS)
        
        await self.add_emoji(msg, emoji)
        
        self.last_mention = time.time()
    
    async def add_emoji(self, msg, emoji_name):
        emoji = discord.utils.get(self.bot.emojis, name=emoji_name)
        await msg.add_reaction(emoji)
    
    def mentioned_in(self, msg):
        tag_mention = str(self.bot.user.id) in msg.content
        name_mention = self.bot.user.name.lower() in msg.content.lower().split()
        return tag_mention or name_mention
    
def contains_words(msg, words):
    words_in_msg = msg.content.lower().split()
    return any(word in words_in_msg for word in words)

def setup(bot):
    bot.add_cog(Cute(bot))