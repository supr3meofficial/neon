import discord
from discord.ext import commands
import asyncio
import datetime
import sys
import traceback
import os
import math

def get_prefix(bot, message):
	"""Bot prefixes"""

	prefixes = ['++','+']

	# DM/Guild check
	if not message.guild:

		pass

	# Guild: Allow mention as prefix
	return commands.when_mentioned_or(*prefixes)(bot, message)


initial_extensions = ['cogs.util',
					  'cogs.owner',
					  'cogs.help',
					  'cogs.games',
					  'cogs.memes',
					  'cogs.caseopening',
					  'cogs.about'
					  #'cogs.test' # DEV only
					  ]

bot = commands.Bot(command_prefix=get_prefix, description='BOT supr3me')

# Load aforementioned cogs
if __name__ == '__main__':
	for extension in initial_extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			print(f'Failed to load extension {extension}.', file=sys.stderr)
			traceback.print_exc()

# Process commands
@bot.event
async def on_message(message):

	await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
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

@bot.event
async def on_error(event, *args, **kwargs):

	print("[ERROR]",sys.exc_info())

def connected_users():

	return str(len(bot.users)) + " users"

@bot.event
async def on_ready():
	"""http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

	print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
	print(f'[INFO] Successfully logged in and booted\n')

	bot.uptime = datetime.datetime.utcnow()

	# Status change
	while True:
        
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(name=connected_users(), type=3))
		await asyncio.sleep(300)
		print("\n[INFO] Changed bot's activity and status")
		await bot.change_presence(status=discord.Status.online, activity=discord.Streaming(name="+help", url="http://twitch.tv/supr3meofficial"))
		await asyncio.sleep(300)
	

bot.run(os.environ['BOT_TOKEN'], bot=True, reconnect=True)
