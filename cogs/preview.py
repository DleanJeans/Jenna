import re

from .common import colors
from discord.ext import commands


JUMP_URL_PATTERN = '(https://discord(?:app)?\.com/channels/\d+/\d+/\d+)'

class Preview(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_converter = commands.MessageConverter()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if not message.guild or message.author == self.bot.user or ctx.command: return

        urls = re.findall(JUMP_URL_PATTERN, message.content)
        for jump_url in urls:
            quoted_message = await self.message_converter.convert(ctx, jump_url)
            author = quoted_message.author

            author_text = f'{author.display_name} #{quoted_message.channel}'
            embed = colors.embed(description=quoted_message.content) \
                    .set_author(name=author_text, icon_url=author.avatar_url) \
                    .add_field(name='Link', value=f'[Jump]({jump_url})')
            
            embed.timestamp = quoted_message.created_at
            for a in quoted_message.attachments:
                embed.set_image(url=a.url)
            
            await ctx.send(embed=embed)
            if quoted_message.embeds:
                await ctx.send(embed=quoted_message.embeds[0])

def setup(bot):
    bot.add_cog(Preview(bot))
