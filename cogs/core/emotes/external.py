from math import ceil
from . import utils
from .. import embed_limit

import colors
import const
import textwrap

NUMBER = '#'
TITLE = 'Available Nitro Emotes'
EMPTY_EMBED = colors.embed(title=TITLE)
EMPTY_EMBED.set_footer(text='Page 1/1')

def split_list(l, parts=2):
    length = len(l)
    return [l[i*length // parts: (i+1)*length // parts] for i in range(parts)]

def get_first_char(name):
    first_char = name[0].upper()
    return first_char if first_char.isalpha() else NUMBER

class EmojiPaginator:
    def __init__(self, Emotes):
        self.Emotes = Emotes
        self.pages = []
        self.ctx = None
        self.last_emoji_count = 0
    
    async def get_page(self, ctx, page=1):
        self.ctx = ctx

        emoji_count = len(self.Emotes.external_emojis)
        if emoji_count != self.last_emoji_count:
            self.emojis_by_alphabet = await self.sort_emojis()
            self.pages = await self.generate_embeds()
        self.last_emoji_count = emoji_count
        
        page = (page-1) % max(len(self.pages), 1)
        embed = self.pages[page]
        embed.color = colors.get_random()
        return embed

    async def sort_emojis(self):
        emojis_by_alphabet = {}
        for name, emoji in self.Emotes.external_emojis.items():
            first_char = get_first_char(name)
            emoji = await self.get_linked_name(emoji)
            emojis_by_alphabet[first_char] = emojis_by_alphabet.get(first_char, []) + [emoji]
        return emojis_by_alphabet

    async def generate_embeds(self):
        pages = []
        embed = EMPTY_EMBED.copy()
        for first_char, emojis in sorted(self.emojis_by_alphabet.items()):
            emojis = sorted(emojis)
            field_name = first_char + const.INVISIBLE # for smaller emojis on mobile
            field_value = const.BULLET.join(emojis)
            
            if len(field_value) <= embed_limit.FIELD_VALUE:
                embed.add_field(name=field_name, value=field_value, inline=False)
            else:
                parts = textwrap.wrap(field_value, embed_limit.FIELD_VALUE)
                parts = [p.strip(const.BULLET[:-1]) for p in parts]
                for i, value in enumerate(parts):
                    name = field_name + str(i+1)
                    embed.add_field(name=name, value=value, inline=False)
            
            if embed_limit.over(embed):
                pages.append(embed)
                last_embed = embed
                embed = EMPTY_EMBED.copy()
                while embed_limit.over(last_embed):
                    last_field = last_embed.fields[-1]
                    last_embed.remove_field(-1)
                    embed.insert_field_at(0, name=last_field.name, value=last_field.value, inline=False)
        else:
            embed.description = 'There is nothing here!'
        
        pages.append(embed)
        for i, embed in enumerate(pages):
            embed.set_footer(text=f'Page {i+1}/{len(pages)}')
        return pages

    async def get_linked_name(self, emoji):
        emoji = await utils.to_partial_emoji(self.ctx, emoji)
        return f'[{emoji.name}]({emoji.url})'