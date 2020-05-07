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
		if isinstance(error, commands.NoPrivateMessage):
			await ctx.author.send('This command cannot be used in private messages.')
		elif isinstance(error, commands.DisabledCommand):
			await ctx.author.send('Sorry. This command is disabled and cannot be used.')
		elif isinstance(error, commands.CommandInvokeError):
			original = error.original
			if not isinstance(original, discord.HTTPException):
				print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
				traceback.print_tb(original.__traceback__)
				print(f'{original.__class__.__name__}: {original}', file=sys.stderr)
		elif isinstance(error, commands.ArgumentParsingError):
			await ctx.send(error)

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
