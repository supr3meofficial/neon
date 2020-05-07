import discord
from discord.ext import commands
import datetime
import traceback
from typing import Union, Optional
import copy
import logging

log = logging.getLogger(__name__)

def get_human_readable_uptime_diff(start_time):

	now = datetime.datetime.utcnow()
	delta = now - start_time
	hours, remainder = divmod(int(delta.total_seconds()), 3600)
	minutes, seconds = divmod(remainder, 60)
	days, hours = divmod(hours, 24)

	if days:
		fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
	else:
		fmt = '{h} hours, {m} minutes, and {s} seconds'

	return fmt.format(d=days, h=hours, m=minutes, s=seconds)

class GlobalChannel(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			return await commands.TextChannelConverter().convert(ctx, argument)
		except commands.BadArgument:
			# Not found... so fall back to ID + global lookup
			try:
				channel_id = int(argument, base=10)
			except ValueError:
				raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
			else:
				channel = ctx.bot.get_channel(channel_id)
				if channel is None:
					raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
				return

class AdminTools(commands.Cog):
	"""Admin only tools"""

	def __init__(self, bot):
		self.bot = bot

	# Admin Tools

	@commands.command(name='load', hidden=True)
	async def moduleload(self, ctx, *, module: str):
		"""Loads a Module"""
		try:
			self.bot.load_extension(module)
		except commands.ExtensionError as e:
			await ctx.send(f'**ADMIN**: {e.__class__.__name__} - {e}')
		else:
			await ctx.send(f'**ADMIN:** Loaded {module}')

	@commands.command(name='unload', hidden=True)
	async def moduleunload(self, ctx, *, module: str):
		"""Unloads a Module"""
		try:
			self.bot.unload_extension(module)
		except commands.ExtensionError as e:
			await ctx.send(f'**ADMIN**: {e.__class__.__name__} - {e}')
		else:
			await ctx.send(f'**ADMIN:** Unloaded {module}')

	@commands.command(name='reload', hidden=True)
	async def modulereload(self, ctx, *, module: str):
		"""Reloads a Module"""
		try:
			self.bot.reload_extension(module)
		except commands.ExtensionError as e:
			await ctx.send(f'**ADMIN**: {e.__class__.__name__} - {e}')
		else:
			await ctx.send(f'**ADMIN:** Reloaded {module}')

	@commands.command(name='spam', aliases=['say'], delete_after=True, hidden=True)
	async def spam(self, ctx, amount, **content : str):
		"""Spams a certain message"""
		if delete_after:
			await ctx.message.delete()
		for spam in range(int(amount)):
			await ctx.send(content)

	@commands.command(hidden=True)
	async def info(self, ctx):
		"""Returns client info"""
		embed = discord.Embed(title='**Client Info**', description='', colour=0xbf0000)
		embed.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.name)
		embed.add_field(name='Users Connected:', value=len(self.bot.users), inline=True)
		embed.add_field(name='Guilds Connected:', value=len(self.bot.guilds), inline=True)
		embed.add_field(name='Current Latency:', value=self.bot.latency, inline=True)
		await ctx.send(embed=embed)

	@commands.command(hidden=True)
	async def servers(self, ctx):
		"""Returns current connected guilds"""
		embed = discord.Embed(title='**Connected Servers:**', description='', colour=0xbf0000)
		embed.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.name)
		for guild in self.bot.guilds:
			embed.add_field(name='\uFEFF', value=guild.name, inline=False)
		await ctx.send(embed=embed)

	def get_bot_uptime(self, *, brief=False):
			return time.human_timedelta(self.bot.uptime, accuracy=None, brief=brief, suffix=False)

	@commands.command(hidden=True)
	async def uptime(self, ctx):
		"""Returns client uptime"""
		def get_bot_uptime():
			return get_human_readable_uptime_diff(self.bot.uptime)
		embed = discord.Embed(title='**Uptime:**', description=self.get_bot_uptime(), colour=0xbf0000)
		embed.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.name)
		await ctx.send(embed=embed)

	@commands.command(hidden=True)
	async def channel(self, ctx):
		"""Returns current channel info"""
		if ctx.channel.is_nsfw():
			nsfw = "NSFW"
		else:
			nsfw = "SFW"

		embed = discord.Embed(title='', description='', colour=0xbf0000)
		embed.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.name)
		embed.add_field(name='**Channel Name:**', value=ctx.channel.name, inline=False)
		embed.add_field(name='**Channel ID:**', value=ctx.channel.id, inline=False)
		embed.add_field(name='**Channel Position:**', value=ctx.channel.position, inline=False)
		embed.add_field(name='**Channel Members:**', value=len(ctx.channel.members), inline=False)
		embed.add_field(name='**Channel NSFW:**', value=nsfw, inline=False)
		embed.add_field(name='**Channel Creation Time:**', value=ctx.channel.created_at, inline=False)
		await ctx.send(embed=embed)

	@commands.command(hidden=True)
	async def member(self, ctx, member: discord.Member=None):
		"""Returns member info"""
		if member is None:
			member = ctx.author
		embed = discord.Embed(title='', description='', colour=0xbf0000)
		embed.set_author(icon_url=member.avatar_url, name=member.name)
		embed.add_field(name='**Member Name:**', value=member.name, inline=False)
		embed.add_field(name='**Member Nickname:**', value=member.nick, inline=False)
		embed.add_field(name='**Member ID:**', value=member.id, inline=False)
		embed.add_field(name='**Member Status:**', value=str(member.status), inline=False)
		embed.add_field(name='**Member Activity:**', value=str(member.activity), inline=False)
		embed.add_field(name='**Member Top Role:**', value=str(member.top_role.name), inline=False)
		embed.add_field(name='**Member Colour:**', value=str(member.colour), inline=False)
		embed.add_field(name='**Member Avatar:**', value=str(member.avatar_url), inline=False)
		await ctx.send(embed=embed)

	@commands.command(name='perms', hidden=True)
	async def check_permissions(self, ctx, *, member: discord.Member=None):
		"""Checks member permissions"""
		if not member:
			member = ctx.author
		perms = '\n'.join(perm for perm, value in member.guild_permissions if value)
		embed = discord.Embed(title='Permissions in:', description=ctx.guild.name, colour=member.colour)
		embed.set_author(icon_url=member.avatar_url, name=str(member))
		embed.add_field(name='\uFEFF', value=perms)
		await ctx.send(content=None, embed=embed)

	@commands.command(hidden=True)
	async def sudo(self, ctx, channel: Optional[GlobalChannel], who: discord.User, *, command: str):
		"""Run a command as another user optionally in another channel."""
		msg = copy.copy(ctx.message)
		channel = channel or ctx.channel
		msg.channel = channel
		msg.author = channel.guild.get_member(who.id) or who
		msg.content = ctx.prefix + command
		new_ctx = await self.bot.get_context(msg, cls=type(ctx))
		new_ctx._db = ctx._db
		await self.bot.invoke(new_ctx)

def setup(bot):
	bot.add_cog(AdminTools(bot))
