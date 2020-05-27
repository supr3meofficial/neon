import discord
from discord.ext import commands
from .utils import time as utiltime
import datetime
import traceback
from typing import Union, Optional
from collections import Counter, defaultdict
import copy
import time
import logging

log = logging.getLogger(__name__)

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

class FetchedUser(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument('Not a valid user ID.')
        try:
            return await ctx.bot.fetch_user(argument)
        except discord.NotFound:
            raise commands.BadArgument('User not found.') from None
        except discord.HTTPException:
            raise commands.BadArgument('An error occurred while fetching the user.') from None

class AdminTools(commands.Cog):
	"""Admin only tools"""

	def __init__(self, bot):
		self.bot = bot

	# Admin Tools

	@commands.command(name='load', hidden=True)
	@commands.is_owner()
	async def moduleload(self, ctx, *, module: str):
		"""Loads a Module"""
		try:
			self.bot.load_extension(module)
		except commands.ExtensionError as e:
			await ctx.send(f'**ADMIN**: {e.__class__.__name__} - {e}')
		else:
			await ctx.send(f'**ADMIN:** Loaded {module}')

	@commands.command(name='unload', hidden=True)
	@commands.is_owner()
	async def moduleunload(self, ctx, *, module: str):
		"""Unloads a Module"""
		try:
			self.bot.unload_extension(module)
		except commands.ExtensionError as e:
			await ctx.send(f'**ADMIN**: {e.__class__.__name__} - {e}')
		else:
			await ctx.send(f'**ADMIN:** Unloaded {module}')

	@commands.command(name='reload', hidden=True)
	@commands.is_owner()
	async def modulereload(self, ctx, *, module: str):
		"""Reloads a Module"""
		try:
			self.bot.reload_extension(module)
		except commands.ExtensionError as e:
			await ctx.send(f'**ADMIN**: {e.__class__.__name__} - {e}')
		else:
			await ctx.send(f'**ADMIN:** Reloaded {module}')

	@commands.command(name='spam', aliases=['say'], hidden=True)
	@commands.is_owner()
	async def spam(self, ctx, amount, delete_after : bool, *, content : str):
		"""Spams a certain message"""
		if delete_after:
			await ctx.message.delete()
		for spam in range(int(amount)):
			await ctx.send(content)

	def get_bot_uptime(self, *, brief=False):
			return utiltime.human_timedelta(self.bot.uptime, accuracy=None, brief=brief, suffix=False)

	@commands.command(hidden=True)
	@commands.is_owner()
	async def uptime(self, ctx):
		"""Returns client uptime"""
		embed = discord.Embed(title='**Uptime:**', description=self.get_bot_uptime(), colour=0xbf0000)
		embed.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.name)
		await ctx.send(embed=embed)

	@commands.command(hidden=True)
	@commands.is_owner()
	async def avatar(self, ctx, *, user: Union[discord.Member, FetchedUser] = None):
		"""Shows a user's enlarged avatar (if possible)."""
		embed = discord.Embed()
		user = user or ctx.author
		avatar = user.avatar_url_as(static_format='png')
		embed.set_author(name=str(user), url=avatar)
		embed.set_image(url=avatar)
		await ctx.send(embed=embed)

	@commands.command(hidden=True)
	@commands.is_owner()
	async def info(self, ctx, *, user: Union[discord.Member, FetchedUser] = None):
		"""Shows info about a user."""

		user = user or ctx.author
		if ctx.guild and isinstance(user, discord.User):
			user = ctx.guild.get_member(user.id) or user

		e = discord.Embed()
		roles = [role.name.replace('@', '@\u200b') for role in getattr(user, 'roles', [])]
		shared = sum(g.get_member(user.id) is not None for g in self.bot.guilds)
		e.set_author(name=str(user))

		def format_date(dt):
			if dt is None:
				return 'N/A'
			return f'{dt:%Y-%m-%d %H:%M} ({utiltime.human_timedelta(dt, accuracy=3)})'

		e.add_field(name='ID', value=user.id, inline=False)
		e.add_field(name='Servers', value=f'{shared} shared', inline=False)
		e.add_field(name='Joined', value=format_date(getattr(user, 'joined_at', None)), inline=False)
		e.add_field(name='Created', value=format_date(user.created_at), inline=False)

		voice = getattr(user, 'voice', None)
		if voice is not None:
			vc = voice.channel
			other_people = len(vc.members) - 1
			voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
			e.add_field(name='Voice', value=voice, inline=False)

		if roles:
			e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles', inline=False)

		colour = user.colour
		if colour.value:
			e.colour = colour

		if user.avatar:
			e.set_thumbnail(url=user.avatar_url)

		if isinstance(user, discord.User):
			e.set_footer(text='This member is not in this server.')

		await ctx.send(embed=e)

	@commands.command(aliases=['guildinfo'], hidden=True)
	@commands.guild_only()
	@commands.is_owner()
	async def serverinfo(self, ctx, *, guild_id: int = None):
		"""Shows info about the current server."""

		if guild_id is not None and await self.bot.is_owner(ctx.author):
			guild = self.bot.get_guild(guild_id)
			if guild is None:
				return await ctx.send(f'Invalid Guild ID given.')
		else:
			guild = ctx.guild

		roles = [role.name.replace('@', '@\u200b') for role in guild.roles]

		# we're going to duck type our way here
		class Secret:
			pass

		secret_member = Secret()
		secret_member.id = 0
		secret_member.roles = [guild.default_role]

		# figure out what channels are 'secret'
		secret = Counter()
		totals = Counter()
		for channel in guild.channels:
			perms = channel.permissions_for(secret_member)
			channel_type = type(channel)
			totals[channel_type] += 1
			if not perms.read_messages:
				secret[channel_type] += 1
			elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
				secret[channel_type] += 1

		member_by_status = Counter(str(m.status) for m in guild.members)

		e = discord.Embed()
		e.title = guild.name
		e.add_field(name='ID', value=guild.id)
		e.add_field(name='Owner', value=guild.owner)
		if guild.icon:
			e.set_thumbnail(url=guild.icon_url)

		channel_info = []
		key_to_emoji = {
			discord.TextChannel: ['<:channel:711201275319943179>', '<:lockedchannel:711201275202633800>'],
			discord.VoiceChannel: ['<:voicechannel:711201275319943219>', ' <:lockedvoicechannel:711201275223605330>'],
		}
		for key, total in totals.items():
			secrets = secret[key]
			try:
				emoji = key_to_emoji[key][0]
				emoji2 = key_to_emoji[key][1]
			except KeyError:
				continue

			if secrets:
				channel_info.append(f'{emoji} {total}\n{emoji2} {secrets}')
			else:
				channel_info.append(f'{emoji} {total}')

		info = []
		features = set(guild.features)
		all_features = {
			'PARTNERED': 'Partnered',
			'VERIFIED': 'Verified',
			'DISCOVERABLE': 'Server Discovery',
			'PUBLIC': 'Server Discovery/Public',
			'INVITE_SPLASH': 'Invite Splash',
			'VIP_REGIONS': 'VIP Voice Servers',
			'VANITY_URL': 'Vanity Invite',
			'MORE_EMOJI': 'More Emoji',
			'COMMERCE': 'Commerce',
			'LURKABLE': 'Lurkable',
			'NEWS': 'News Channels',
			'ANIMATED_ICON': 'Animated Icon',
			'BANNER': 'Banner'
		}

		for feature, label in all_features.items():
			if feature in features:
				info.append(f'{ctx.tick(True)}: {label}')

		if info:
			e.add_field(name='Features', value='\n'.join(info))

		e.add_field(name='Channels', value='\n'.join(channel_info), inline=False)

		if guild.premium_tier != 0:
			boosts = f'Level {guild.premium_tier}\n{guild.premium_subscription_count} boosts'
			last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
			if last_boost.premium_since is not None:
				boosts = f'{boosts}\nLast Boost: {last_boost} ({utiltime.human_timedelta(last_boost.premium_since, accuracy=2)})'
			e.add_field(name='Boosts', value=boosts, inline=False)

		fmt = f'👤 Total: {guild.member_count} \n\n' \
		f'<:online:711201275353497671> {member_by_status["online"]} ' \
		f'<:idle:711201275202502658> {member_by_status["idle"]} ' \
		f'<:dnd:711201275110490177> {member_by_status["dnd"]} ' \
		f'<:offline:711201275412217896> {member_by_status["offline"]}'

		e.add_field(name='Members', value=fmt, inline=False)
		e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')
		e.set_footer(text='Created').timestamp = guild.created_at
		await ctx.send(embed=e)

	async def say_permissions(self, ctx, member, channel):
		permissions = channel.permissions_for(member)
		e = discord.Embed(colour=member.colour)
		avatar = member.avatar_url_as(static_format='png')
		e.set_author(name=str(member), url=avatar)
		allowed, denied = [], []
		for name, value in permissions:
			name = name.replace('_', ' ').replace('guild', 'server').title()
			if value:
				allowed.append(name)
			else:
				denied.append(name)

		e.add_field(name='Allowed', value='\n'.join(allowed))
		e.add_field(name='Denied', value='\n'.join(denied))
		await ctx.send(embed=e)

	@commands.command(hidden=True)
	@commands.guild_only()
	@commands.is_owner()
	async def permissions(self, ctx, member: discord.Member = None, channel: discord.TextChannel = None):
		"""Shows a member's permissions in a specific channel.

		If no channel is given then it uses the current one.

		You cannot use this in private messages. If no member is given then
		the info returned will be yours.
		"""
		channel = channel or ctx.channel
		if member is None:
			member = ctx.author

		await self.say_permissions(ctx, member, channel)

	@commands.command(hidden=True)
	@commands.guild_only()
	@commands.is_owner()
	async def botpermissions(self, ctx, *, channel: discord.TextChannel = None):
		"""Shows the bot's permissions in a specific channel.

		If no channel is given then it uses the current one.

		This is a good way of checking if the bot has the permissions needed
		to execute the commands it wants to execute.

		To execute this command you must have Manage Roles permission.
		You cannot use this in private messages.
		"""
		channel = channel or ctx.channel
		member = ctx.guild.me
		await self.say_permissions(ctx, member, channel)

	@commands.command(hidden=True)
	@commands.is_owner()
	async def debugpermissions(self, ctx, guild_id: int, channel_id: int, author_id: int = None):
		"""Shows permission resolution for a channel and an optional author."""

		guild = self.bot.get_guild(guild_id)
		if guild is None:
			return await ctx.send('Guild not found?')

		channel = guild.get_channel(channel_id)
		if channel is None:
			return await ctx.send('Channel not found?')

		if author_id is None:
			member = guild.me
		else:
			member = guild.get_member(author_id)

		if member is None:
			return await ctx.send('Member not found?')

		await self.say_permissions(ctx, member, channel)

	@commands.command(hidden=True)
	@commands.is_owner()
	async def sudo(self, ctx, channel: Optional[GlobalChannel], who: discord.User, *, command: str):
		"""Run a command as another user optionally in another channel."""
		msg = copy.copy(ctx.message)
		channel = channel or ctx.channel
		msg.channel = channel
		msg.author = channel.guild.get_member(who.id) or who
		msg.content = ctx.prefix + command
		new_ctx = await self.bot.get_context(msg, cls=type(ctx))
		await self.bot.invoke(new_ctx)

def setup(bot):
	bot.add_cog(AdminTools(bot))
