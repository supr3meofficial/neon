from discord.ext import commands, tasks
from .utils import checks, time, cache
#from .utils.db import Database
from .utils.formats import plural
from collections import Counter, defaultdict
from inspect import cleandoc

import re
import json
import discord
import enum
import datetime
import asyncio
import argparse, shlex
import logging
import io

log = logging.getLogger(__name__)

# Converters

class MemberID(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			m = await commands.MemberConverter().convert(ctx, argument)
		except commands.BadArgument:
			try:
				member_id = int(argument, base=10)
				m = await resolve_member(ctx.guild, member_id)
			except ValueError:
				raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
			except MemberNotFound:
				# hackban case
				return type('_Hackban', (), {'id': member_id, '__str__': lambda s: f'Member ID {s.id}'})()

		if not can_execute_action(ctx, ctx.author, m):
			raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
		return m

class BannedMember(commands.Converter):
	async def convert(self, ctx, argument):
		ban_list = await ctx.guild.bans()
		try:
			member_id = int(argument, base=10)
			entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
		except ValueError:
			entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

		if entity is None:
			raise commands.BadArgument("Not a valid previously-banned member.")
		return entity

class ActionReason(commands.Converter):
	async def convert(self, ctx, argument):
		ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'

		if len(ret) > 512:
			reason_max = 512 - len(ret) + len(argument)
			raise commands.BadArgument(f'Reason is too long ({len(argument)}/{reason_max})')
		return ret

# cog

class ModTools(commands.Cog):
	"""Moderation related commands."""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases=['newmembers'])
	@commands.guild_only()
	async def newusers(self, ctx, *, count=5):
		"""Tells you the newest members of the server.

		This is useful to check if any suspicious members have
		joined.

		The count parameter can only be up to 25.
		"""
		count = max(min(count, 25), 5)

		if not ctx.guild.chunked:
			await self.bot.request_offline_members(ctx.guild)

		members = sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=True)[:count]

		e = discord.Embed(title='New Members', colour=discord.Colour.green())

		for member in members:
			body = f'Joined {time.human_timedelta(member.joined_at)}\nCreated {time.human_timedelta(member.created_at)}'
			e.add_field(name=f'{member} (ID: {member.id})', value=body, inline=False)

		await ctx.send(embed=e)

	async def _basic_cleanup_strategy(self, ctx, search):
		count = 0
		async for msg in ctx.history(limit=search, before=ctx.message):
			if msg.author == ctx.me:
				await msg.delete()
				count += 1
		return { 'Bot': count }

	async def _complex_cleanup_strategy(self, ctx, search):
		prefixes = tuple(self.bot.get_guild_prefixes(ctx.guild)) # thanks startswith

		def check(m):
			return m.author == ctx.me or m.content.startswith(prefixes)

		deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
		return Counter(m.author.display_name for m in deleted)

	@commands.command()
	@checks.has_permissions(manage_messages=True)
	async def cleanup(self, ctx, search=100):
		"""Cleans up the bot's messages from the channel.

		If a search number is specified, it searches that many messages to delete.
		If the bot has Manage Messages permissions then it will try to delete
		messages that look like they invoked the bot as well.

		After the cleanup is completed, the bot will send you a message with
		which people got their messages deleted and their count. This is useful
		to see which users are spammers.

		You must have Manage Messages permission to use this.
		"""

		strategy = self._basic_cleanup_strategy
		if ctx.me.permissions_in(ctx.channel).manage_messages:
			strategy = self._complex_cleanup_strategy

		spammers = await strategy(ctx, search)
		deleted = sum(spammers.values())
		messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
		if deleted:
			messages.append('')
			spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
			messages.extend(f'- **{author}**: {count}' for author, count in spammers)

		await ctx.send('\n'.join(messages), delete_after=10)

	@commands.command()
	@commands.guild_only()
	@checks.has_permissions(kick_members=True)
	async def kick(self, ctx, member: MemberID, *, reason: ActionReason = None):
		"""Kicks a member from the server.

		In order for this to work, the bot must have Kick Member permissions.

		To use this command you must have Kick Members permission.
		"""

		if reason is None:
			reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

		await ctx.guild.kick(member, reason=reason)

		embed = discord.Embed(title='',
		description="<:BanHammer:439943003847786499> {member} has been kicked",
		colour=ctx.author.colour)
		embed.set_author(icon_url=member.avatar_url, name=user_banned)

		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	@checks.has_permissions(ban_members=True)
	async def ban(self, ctx, member: MemberID, *, reason: ActionReason = None):
		"""Bans a member from the server.

		You can also ban from ID to ban regardless whether they're
		in the server or not.

		In order for this to work, the bot must have Ban Member permissions.

		To use this command you must have Ban Members permission.
		"""

		if reason is None:
			reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

		await ctx.guild.ban(member, reason=reason)

		embed = discord.Embed(title='',
		description="<:BanHammer:439943003847786499> `{member}` has been banned",
		colour=ctx.author.colour)
		embed.set_author(icon_url=member.avatar_url, name=user_banned)

		await ctx.send('\N{OK HAND SIGN}')

	@commands.command()
	@commands.guild_only()
	@checks.has_permissions(ban_members=True)
	async def multiban(self, ctx, members: commands.Greedy[MemberID], *, reason: ActionReason = None):
		"""Bans multiple members from the server.

		This only works through banning via ID.

		In order for this to work, the bot must have Ban Member permissions.

		To use this command you must have Ban Members permission.
		"""

		if reason is None:
			reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

		total_members = len(members)
		if total_members == 0:
			return await ctx.send('Missing members to ban.')

		confirm = await ctx.prompt(f'This will ban **{plural(total_members):member}**. Are you sure?', reacquire=False)
		if not confirm:
			return await ctx.send('Aborting.')

		failed = 0
		for member in members:
			try:
				await ctx.guild.ban(member, reason=reason)
			except discord.HTTPException:
				failed += 1

		embed = discord.Embed(title='',
		description=f"<:BanHammer:439943003847786499> Banned {total_members - failed}/{total_members} members.",
		colour=ctx.author.colour)
		embed.set_author(icon_url=member.avatar_url, name=user_banned)

		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	@checks.has_permissions(ban_members=True)
	async def massban(self, ctx, *, args):
		"""Mass bans multiple members from the server.

		This command has a powerful "command line" syntax. To use this command
		you and the bot must both have Ban Members permission. **Every option is optional.**

		Users are only banned **if and only if** all conditions are met.

		The following options are valid.

		`--channel` or `-c`: Channel to search for message history.
		`--reason` or `-r`: The reason for the ban.
		`--regex`: Regex that usernames must match.
		`--created`: Matches users whose accounts were created less than specified minutes ago.
		`--joined`: Matches users that joined less than specified minutes ago.
		`--joined-before`: Matches users who joined before the member ID given.
		`--joined-after`: Matches users who joined after the member ID given.
		`--no-avatar`: Matches users who have no avatar. (no arguments)
		`--no-roles`: Matches users that have no role. (no arguments)
		`--show`: Show members instead of banning them (no arguments).

		Message history filters (Requires `--channel`):

		`--contains`: A substring to search for in the message.
		`--starts`: A substring to search if the message starts with.
		`--ends`: A substring to search if the message ends with.
		`--match`: A regex to match the message content to.
		`--search`: How many messages to search. Default 100. Max 2000.
		`--after`: Messages must come after this message ID.
		`--before`: Messages must come before this message ID.
		`--files`: Checks if the message has attachments (no arguments).
		`--embeds`: Checks if the message has embeds (no arguments).
		"""

		# For some reason there are cases due to caching that ctx.author
		# can be a User even in a guild only context
		# Rather than trying to work out the kink with it
		# Just upgrade the member itself.
		if not isinstance(ctx.author, discord.Member):
			try:
				author = await ctx.guild.fetch_member(ctx.author.id)
			except discord.HTTPException:
				return await ctx.send('Somehow, Discord does not seem to think you are in this server.')
		else:
			author = ctx.author

		parser = Arguments(add_help=False, allow_abbrev=False)
		parser.add_argument('--channel', '-c')
		parser.add_argument('--reason', '-r')
		parser.add_argument('--search', type=int, default=100)
		parser.add_argument('--regex')
		parser.add_argument('--no-avatar', action='store_true')
		parser.add_argument('--no-roles', action='store_true')
		parser.add_argument('--created', type=int)
		parser.add_argument('--joined', type=int)
		parser.add_argument('--joined-before', type=int)
		parser.add_argument('--joined-after', type=int)
		parser.add_argument('--contains')
		parser.add_argument('--starts')
		parser.add_argument('--ends')
		parser.add_argument('--match')
		parser.add_argument('--show', action='store_true')
		parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
		parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
		parser.add_argument('--after', type=int)
		parser.add_argument('--before', type=int)

		try:
			args = parser.parse_args(shlex.split(args))
		except Exception as e:
			return await ctx.send(str(e))

		members = []

		if args.channel:
			channel = await commands.TextChannelConverter().convert(ctx, args.channel)
			before = args.before and discord.Object(id=args.before)
			after = args.after and discord.Object(id=args.after)
			predicates = []
			if args.contains:
				predicates.append(lambda m: args.contains in m.content)
			if args.starts:
				predicates.append(lambda m: m.content.startswith(args.starts))
			if args.ends:
				predicates.append(lambda m: m.content.endswith(args.ends))
			if args.match:
				try:
					_match = re.compile(args.match)
				except re.error as e:
					return await ctx.send(f'Invalid regex passed to `--match`: {e}')
				else:
					predicates.append(lambda m, x=_match: x.match(m.content))
			if args.embeds:
				predicates.append(args.embeds)
			if args.files:
				predicates.append(args.files)

			async for message in channel.history(limit=min(max(1, args.search), 2000), before=before, after=after):
				if all(p(message) for p in predicates):
					members.append(message.author)
		else:
			members = ctx.guild.members

		# member filters
		predicates = [
			lambda m: isinstance(m, discord.Member) and can_execute_action(ctx, author, m), # Only if applicable
			lambda m: not m.bot, # No bots
			lambda m: m.discriminator != '0000', # No deleted users
		]

		async def _resolve_member(member_id):
			r = ctx.guild.get_member(member_id)
			if r is None:
				try:
					return await ctx.guild.fetch_member(member_id)
				except discord.HTTPException as e:
					raise commands.BadArgument(f'Could not fetch member by ID {member_id}: {e}') from None
			return r

		if args.regex:
			try:
				_regex = re.compile(args.regex)
			except re.error as e:
				return await ctx.send(f'Invalid regex passed to `--regex`: {e}')
			else:
				predicates.append(lambda m, x=_regex: x.match(m.name))

		if args.no_avatar:
			predicates.append(lambda m: m.avatar is None)
		if args.no_roles:
			predicates.append(lambda m: len(getattr(m, 'roles', [])) <= 1)

		now = datetime.datetime.utcnow()
		if args.created:
			def created(member, *, offset=now - datetime.timedelta(minutes=args.created)):
				return member.created_at > offset
			predicates.append(created)
		if args.joined:
			def joined(member, *, offset=now - datetime.timedelta(minutes=args.joined)):
				if isinstance(member, discord.User):
					# If the member is a user then they left already
					return True
				return member.joined_at and member.joined_at > offset
			predicates.append(joined)
		if args.joined_after:
			_joined_after_member = await _resolve_member(args.joined_after)
			def joined_after(member, *, _other=_joined_after_member):
				return member.joined_at and _other.joined_at and member.joined_at > _other.joined_at
			predicates.append(joined_after)
		if args.joined_before:
			_joined_before_member = await _resolve_member(args.joined_before)
			def joined_before(member, *, _other=_joined_before_member):
				return member.joined_at and _other.joined_at and member.joined_at < _other.joined_at
			predicates.append(joined_before)

		members = {m for m in members if all(p(m) for p in predicates)}
		if len(members) == 0:
			return await ctx.send('No members found matching criteria.')

		if args.show:
			members = sorted(members, key=lambda m: m.joined_at or now)
			fmt = "\n".join(f'{m.id}\tJoined: {m.joined_at}\tCreated: {m.created_at}\t{m}' for m in members)
			content = f'Current Time: {datetime.datetime.utcnow()}\nTotal members: {len(members)}\n{fmt}'
			file = discord.File(io.BytesIO(content.encode('utf-8')), filename='members.txt')
			return await ctx.send(file=file)

		if args.reason is None:
			return await ctx.send('--reason flag is required.')
		else:
			reason = await ActionReason().convert(ctx, args.reason)

		confirm = await ctx.prompt(f'This will ban **{plural(len(members)):member}**. Are you sure?')
		if not confirm:
			return await ctx.send('Aborting.')

		count = 0
		for member in members:
			try:
				await ctx.guild.ban(member, reason=reason)
			except discord.HTTPException:
				pass
			else:
				count += 1

		await ctx.send(f'Banned {count}/{len(members)}')

	@commands.command()
	@commands.guild_only()
	@checks.has_permissions(kick_members=True)
	async def softban(self, ctx, member: MemberID, *, reason: ActionReason = None):
		"""Soft bans a member from the server.

		A softban is basically banning the member from the server but
		then unbanning the member as well. This allows you to essentially
		kick the member while removing their messages.

		In order for this to work, the bot must have Ban Member permissions.

		To use this command you must have Kick Members permissions.
		"""

		if reason is None:
			reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

		await ctx.guild.ban(member, reason=reason)
		await ctx.guild.unban(member, reason=reason)

		embed = discord.Embed(title='',
		description=f"<:BanHammer:439943003847786499> Soft banned {member}",
		colour=ctx.author.colour)
		embed.set_author(icon_url=member.avatar_url, name=user_banned)

		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	@checks.has_permissions(ban_members=True)
	async def unban(self, ctx, member: BannedMember, *, reason: ActionReason = None):
		"""Unbans a member from the server.

		You can pass either the ID of the banned member or the Name#Discrim
		combination of the member. Typically the ID is easiest to use.

		In order for this to work, the bot must have Ban Member permissions.

		To use this command you must have Ban Members permissions.
		"""

		if reason is None:
			reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

		await ctx.guild.unban(member.user, reason=reason)
		if member.reason:
			r = f'Unbanned {member.user} (ID: {member.user.id}), previously banned for {member.reason}'
		else:
			r = f'Unbanned {member.user} (ID: {member.user.id})'

		if r:
			embed = discord.Embed(title='',
			description=r,
			colour=ctx.author.colour)
			embed.set_author(icon_url=member.avatar_url, name=user_banned)
			await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(ModTools(bot))
