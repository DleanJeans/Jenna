import discord

from discord.ext import commands

class NitroEmojiConverter(commands.PartialEmojiConverter):
    async def convert(self, ctx, arg):
        no_colon = arg.replace(':', '')
        emoji = get_known_emoji(ctx.bot.emojis, no_colon, ctx.author)
        if not emoji:
            try: emoji = await super().convert(ctx, arg)
            except: emoji = no_colon
        return emoji

def get_known_emoji(emojis, name, user=None):
    def score_relevance(emoji):
        try:
            in_guild = emoji.guild in user.mutual_guilds
            total_score = in_guild * 100
            if in_guild:
                member = emoji.guild.get_member(user.id)
                sum_roles = sum([r.position for r in member.roles])
                is_owner = emoji.guild.owner == member
                total_score += sum_roles + is_owner * 100
            return total_score
        except:
            return 0

    duplicates = [e for e in emojis if e.name == name]
    duplicates.sort(key=score_relevance, reverse=True)
    return duplicates[0] if duplicates else None
    return discord.utils.get(emojis, name=name)

emoji_converter = NitroEmojiConverter()
async def convert(ctx, arg):
    return await emoji_converter.convert(ctx, arg)