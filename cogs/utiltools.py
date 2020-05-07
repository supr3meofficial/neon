import discord
import random
from discord.ext import commands
import aiohttp
import asyncio
from typing import Union, Optional
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

class UtilTools(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.guild_only()
	async def joined(self, ctx, *, member: discord.Member):
		"""Returns the mentioned user's guild join date"""
		date = str(member.joined_at).split(".")[0]
		requested_by = "Requested by {}".format(ctx.author.name)

		embed = discord.Embed(title="", description="", colour=ctx.author.colour)
		embed.set_author(icon_url=member.avatar_url, name=str(member))
		embed.set_thumbnail(url="https://twemoji.maxcdn.com/2/72x72/1f552.png")
		embed.add_field(name="Join Date:", value=date, inline=False)
		embed.set_footer(text=requested_by)

		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def ping(self, ctx):
		"""Returns current bot latency in ms"""
		member = ctx.author
		requested_by = f"Requested by {ctx.author.name}"
		latency = '{0}'.format(round(self.bot.latency, 1))
		desc = f'{latency} ms'

		embed = discord.Embed(title="", description="", colour=member.colour)
		embed.set_author(icon_url=self.bot.user.avatar_url, name=str(self.bot.user.name))
		embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/439905517280690176.png")
		embed.add_field(name="Latency:", value=desc, inline=False)
		embed.set_footer(text=requested_by)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def spotify(self, ctx, member: discord.Member):
		"""Displays the current song the user is listening to"""

		try:
			 spotify = member.activities[1] # Check if user is listening to Spotify
			 requested_by = f"Requested by {ctx.author.name}"
			 listener = f"{member.name} is listening to:"
			 duration = str(spotify.duration).split(".")[0]
			 artists = str(spotify.artist).replace(";",",")
			 SPOTIFY_ICON = 'https://images-eu.ssl-images-amazon.com/images/I/51rttY7a%2B9L.png'

			 embed = discord.Embed(title="", description="", colour=spotify.colour)
			 embed.set_author(icon_url=SPOTIFY_ICON, name=listener)
			 embed.set_thumbnail(url=spotify.album_cover_url)
			 embed.add_field(name="Title:", value=spotify.title, inline=False)
			 embed.add_field(name="Artists:", value=artists, inline=False)
			 embed.add_field(name="Album:", value=spotify.album, inline=False)
			 embed.add_field(name="Duration:", value=duration, inline=False)
			 embed.set_footer(text=requested_by)
			 await ctx.send(embed=embed)
		except:
			return await ctx.send("User is not listening to Spotify :(",delete_after=5)


	@commands.command(name='createinvite',aliases=['createinv'])
	@commands.guild_only()
	async def _create_invite(self, ctx, channel: Optional[GlobalChannel]):
		"""Creates an invite for a channel"""
		requested_by = f"Requested by {ctx.author.name}"
		channel = ctx.channel
		inv = await channel.create_invite(reason="Created via command")
		embed = discord.Embed(title="Invite Created", description=inv.url, color=ctx.author.colour)
		embed.set_thumbnail(url="https://twemoji.maxcdn.com/2/72x72/1f517.png")
		embed.set_footer(text=requested_by)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def roll(self, ctx, minimum=0, maximum=100):
		"""Rolls a random number within an optional range. Max: 1000"""
		member = ctx.author

		maximum = min(maximum, 1000)
		if minimum >= maximum:
			await ctx.send('Maximum is smaller than minimum.')
			return
		roll = random.randint(minimum,maximum)

		embed = discord.Embed(title="", description="", colour=member.colour)
		embed.set_author(icon_url=member.avatar_url, name=str(member))
		embed.set_thumbnail(url="https://twemoji.maxcdn.com/2/72x72/1f3b2.png")
		embed.add_field(name="Rolled:", value=roll, inline=True)
		embed.add_field(name="Max:", value=maximum, inline=True)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def choose(self, ctx, *choices : str):
		"""Chooses between multiple choices"""
		member = ctx.author
		choice = random.choice(choices)

		embed = discord.Embed(title="", description="", colour=member.colour)
		embed.set_author(icon_url=member.avatar_url, name=str(member))
		embed.set_thumbnail(url="https://twemoji.maxcdn.com/2/72x72/1f3b2.png")
		embed.add_field(name="Chose:", value=choice, inline=True)
		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(UtilTools(bot))
