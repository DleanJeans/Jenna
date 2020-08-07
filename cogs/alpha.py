import discord
import re
import const
import cogs
import importlib
import sys
import traceback
import colors

from discord.ext import commands
from typing import Optional

ALL = 'all'
EXIT_METHODS = ['quit()', 'exit()']
def is_tick(s):
    if s == '`':
        return True
    raise commands.BadArgument('No backticks!')

class Alpha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        x = reaction.emoji == '🗑️'
        owner_react = user == self.bot.owner
        my_message = reaction.message.author == self.bot.user
        if x and owner_react and my_message:
            await reaction.message.delete()

    @commands.command(aliases=['e', 'exec'])
    @commands.is_owner()
    async def eval(self, context, tick:Optional[is_tick]=False, *, code=None):
        import math, random

        oneliner = code
        def check(m):
            return m.author == context.author and m.channel == context.channel
        if not oneliner:
            await context.send('```>>>```')
        msg = None
        while True:
            if not oneliner:
                msg = await self.bot.wait_for('message', check=check)
                code = msg.content
                if code in EXIT_METHODS:
                    await context.send('```<<<```')
                    break

            try:
                asynchronous = code.startswith('await ')
                code = code.replace('await ', '')
                try:
                    output = eval(code)
                except:
                    output = exec(code)
                if asynchronous:
                    output = await output
                title = ''
            except Exception as e:
                output = e
                title = '⚠️ **Error**:'

            if not oneliner and output == None:
                await msg.add_reaction('✅')
            else:
                if tick:
                    output = f'```{output}```'
                content = f'{title}\n{output}'
                if len(content) > 2000:
                    content = content[:2000-6] + '...'
                    if tick:
                        content += '```'
                embed = colors.embed(description=content)
                await context.send(embed=embed)

            if oneliner:
                break
        
    @commands.command(aliases=['rlm'])
    @commands.is_owner()
    async def reloadmodule(self, context, *, module=ALL):
        await context.trigger_typing()
        responses = []
        core_modules = [(name, module) for name, module in sys.modules.items() if name.startswith('cogs.')]
        if module == ALL:
            reloaded_modules = core_modules
        else:
            modules = module.split()
            reloaded_modules = filter(lambda m: any(rm in m[0] for rm in modules), core_modules)
        
        for name, module in reloaded_modules:
            name = name.replace('cogs.', '')
            name = f'Module `{name}`'
            try:
                importlib.reload(module)
                response = f'✅ {name} reloaded!'
            except:
                traceback.print_exc()
                response = f'⚠️ {name} reload failed!'
            responses += [response]
        
        content = '\n'.join(responses) if responses else f'⚠️ No modules named `{module}`!'
        await context.send(content)

    @commands.command(aliases=['rl', 'rlc'])
    @commands.is_owner()
    async def reloadcog(self, context, *, cog=ALL):
        await context.trigger_typing()
        responses = []
        cog = cogs.NAMES if cog == ALL else cog.split()
        
        for cog_name in cog:
            cog_path = 'cogs.' + cog_name
            response = 'Cog `%s`' % cog_name

            try:
                self.bot.reload_extension(cog_path)
                response = f'✅ {response} reloaded!'
            except:
                traceback.print_exc()
                response = f'⚠️ {response} reload failed!'
             
            responses += [response]

        content = '\n'.join(responses)
        await context.send(content)
    
    @commands.command()
    async def clearuntil(self, context, message:discord.Message):
        await context.trigger_typing()
        msgs_to_clear = await context.history(after=message).flatten()
        await context.channel.delete_messages(msgs_to_clear)
        await context.send(f'Deleted `{len(msgs_to_clear)}` messages!', delete_after=3)

    @commands.command(aliases=['rp'])
    @commands.is_owner()
    async def repeat(self, context, msg:discord.Message):
        await context.trigger_typing()
        embed = msg.embeds[0] if msg.embeds else None
        files = [await a.to_file() for a in msg.attachments]
        await context.send(msg.content, embed=embed, files=files)
    
    @commands.command()
    async def clean(self, context, limit:Optional[int]=1, *, content=''):
        is_dm = type(context.channel) is discord.DMChannel
        is_owner = await self.bot.is_owner(context.author)
        allowed = is_owner or is_dm
        if not allowed: return

        def is_me(m):
            return m.author == self.bot.user
        progress_msg = await context.send('Deleting...')
        
        msgs_to_delete = []
        deleted = 0
        async for m in context.history(limit=None):
            if is_me(m) and m.id != progress_msg.id and content in m.content:
                msgs_to_delete += [m]
                deleted += 1
                if deleted >= limit:
                    break
        
        permissions = context.channel.permissions_for(context.me)
        if is_dm or not permissions.manage_messages:
            for i, m in enumerate(msgs_to_delete):
                await m.delete()
                await progress_msg.edit(content=f'Deleted `{i+1}/{len(msgs_to_delete)}` messages!')
        else:
            await context.channel.delete_messages(msgs_to_delete)
            await progress_msg.edit(content=f'Deleted `{len(msgs_to_delete)}` messages!')
        
        await progress_msg.edit(delete_after=3)

def setup(bot):
    bot.add_cog(Alpha(bot))
