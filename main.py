import discord
from discord.ext import commands
from cogs.utils import checks
#from cogs.utils.db import Database
import datetime, re
import json, asyncio
import copy
import logging
import sys
import traceback
import os
import aiohttp
import math
from collections import Counter, deque, defaultdict
import config


description = """
Hello! I am Neon :)
"""

log = logging.getLogger(__name__)

def _prefix_callable(bot, msg):
	"""Set bot prefixes"""
	prefixes = ['+','++']
	if not msg.guild: pass
	return commands.when_mentioned_or(*prefixes)(bot, msg)

initial_extensions = ['cogs.utiltools',
					  'cogs.admintools',
					  'cogs.modtools',
					  'cogs.minigames',
					  'cogs.fun',
					  'cogs.caseopening',
					  'cogs.aboutlinks',
					  'cogs.help'
					  ]

class Neon(commands.Bot):

	def __init__(self):
		super().__init__(command_prefix=_prefix_callable, description=description,
						 pm_help=None, help_attrs=dict(hidden=True),
						 fetch_offline_members=False, heartbeat_timeout=150.0)

		self.client_id = config.client_id

		# Bot presence Status
		self.status = discord.Activity(name=f'{config.bot_version}!', type=2)

		for extension in initial_extensions:
			try:
				self.load_extension(extension)
			except Exception as e:
				print(f'Failed to load extension {extension}.', file=sys.stderr)
				traceback.print_exc()

	async def on_command_error(self, ctx, error):
	    # Return in local command handler
	    if hasattr(ctx.command, 'on_error'):
	        return

	    # Get the original exception
	    error = getattr(error, 'original', error)

	    if isinstance(error, commands.CommandNotFound):
	        return

	    if isinstance(error, commands.BotMissingPermissions):
	        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
	        if len(missing) > 2:
	            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
	        else:
	            fmt = ' and '.join(missing)
	        _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
	        embed = discord.Embed(title="No permissions",
			description=_message,
			colour=0xbf0000)
	        embed.set_author(icon_url=bot.user.avatar_url, name=bot.user.name)
	        await ctx.send(embed=embed)
	        return

	    if isinstance(error, commands.DisabledCommand):
	        await ctx.send('This command has been disabled.')
	        return

	    if isinstance(error, commands.CommandOnCooldown):
	        msg="This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after))
	        embed = discord.Embed(title="Cooling Down",
	        description=msg,
	        colour=0xbf0000)
	        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author)
	        await ctx.send(embed=embed)
	        return

	    if isinstance(error, commands.MissingPermissions):
	        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
	        if len(missing) > 2:
	            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
	        else:
	            fmt = ' and '.join(missing)
	        _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
	        embed = discord.Embed(title="No permissions",
			description=_message,
			colour=0xbf0000)
	        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author)
	        await ctx.send(embed=embed)
	        return

	    if isinstance(error, discord.Forbidden):
	        embed = discord.Embed(title="No permissions",
	        description="You do not have permission to perform this command",
	        colour=0xbf0000)
	        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author)
	        await ctx.send(embed=embed)

	    if isinstance(error, commands.UserInputError):
	        embed = discord.Embed(title="Invalid input",
					description="Please re-check your command and try again",
					colour=0xbf0000)
	        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
	        await ctx.send(embed=embed)
	        return

	    if isinstance(error, commands.NoPrivateMessage):
	        try:
	            await ctx.author.send('This command cannot be used in direct messages.')
	        except discord.Forbidden:
	            pass
	        return

	    if isinstance(error, commands.CheckFailure):
	        embed = discord.Embed(title="Invalid input",
					description="You do not have permission to use this command.",
					colour=0xbf0000)
	        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
	        await ctx.send(embed=embed)
	        return

	    # Ignore all other exception types, but print them to stderr
	    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)

	    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

	async def on_ready(self):
		if not hasattr(self, 'uptime'):
			self.uptime = datetime.datetime.utcnow()
		await self.change_presence(status=discord.Status.online, activity=self.status)

		print(f'Ready: {self.user} (ID: {self.user.id})')

	async def on_message(self, message):
		if message.author.bot:
			return
		await self.process_commands(message)

	async def close(self):
		await super().close()

	def run(self):
		super().run(config.token, reconnect=True)

	@property
	def config(self):
		return __import__('config')
