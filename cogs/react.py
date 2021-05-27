import discord
import typing
import asyncio

from discord.ext import commands
from collections.abc import Iterable
from .core import converter

X = '❌'
OK = '✅'

class Reactable:
    def __init__(self, msg, users=[]):
        if not isinstance(users, Iterable):
            users = [users]
        self.msg = msg
        self.users = users
        self.callbacks_by_emoji = {}
    
    def add_button(self, emoji, callback):
        self.callbacks_by_emoji[emoji] = callback
    
    def get_callback(self, reaction, user):
        if self.users and user not in self.users:
            return
        for emoji, callback in self.callbacks_by_emoji.items():
            if reaction.emoji == emoji:
                return callback

class React(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactables = {}
    
    async def delete(self, reaction, user):
        try:
            message = reaction.message
            await message.delete()
            self.remove_reactable(message)
        except discord.errors.Forbidden:
            error_msg = await message.channel.send(f'I need `Manage Messages` permission to {X} delete your message.', delete_after=60)
            await self.add_delete_button(error_msg)
    
    def remove_reactable(self, message):
        if message.id in self.reactables:
            self.reactables.pop(message.id)
        
    async def add_delete_button(self, message, users=[], emote=X, delete_after=0):
        await self.add_button(message, emote, self.delete, users)
        if delete_after:
            await asyncio.sleep(delete_after)
            await message.remove_reaction(emote, self.bot.user)
            self.remove_reactable(message)

    async def add_buttons(self, message, emojis, callback, users=[]):
        try:
            for e in emojis:
                await self.add_button(message, e, callback, users)
        except:
            pass # message deleted while adding

    async def add_button(self, message, emoji, callback, users=[]):
        if message.id not in self.reactables:
            self.reactables[message.id] = Reactable(message, users)
        reactable = self.reactables[message.id]
        emoji = await self.add_reaction(message, emoji)
        reactable.add_button(emoji, callback)
    
    async def add_reaction(self, message, emoji):
        context = await self.bot.get_context(message)
        emoji = await converter.emoji(context, emoji)
        await message.add_reaction(emoji)
        return emoji

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        await self.process_reaction(reaction, user)
    
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        await self.process_reaction(reaction, user)

    async def process_reaction(self, reaction, user):
        if user.bot: return

        reactable = self.reactables.get(reaction.message.id)
        if not reactable: return

        callback = reactable.get_callback(reaction, user)
        if callback:
            await callback(reaction, user)

def setup(bot):
    bot.add_cog(React(bot))