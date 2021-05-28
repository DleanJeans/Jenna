import random
import time
import discord
import csv

FILE = 'cogs/common/materialcolors.csv'
with open(FILE) as file:
    reader = csv.reader(file, delimiter='|')
    COLORS_DICT = { name: int(h, 16) for name, h in reader}
    COLORS = list(COLORS_DICT.values())

def get_random(exceptions=None):
    if type(exceptions) is not list:
        exceptions = [exceptions]
    while True:
        random.seed(time.time())
        new_color = random.choice(COLORS)
        if new_color not in exceptions:
            return new_color

def embed(*, color=None, **kwargs):
    return discord.Embed(color=color or get_random(), **kwargs)

def embed_error(**kwargs):
    return discord.Embed(color=discord.Color.red(), **kwargs)