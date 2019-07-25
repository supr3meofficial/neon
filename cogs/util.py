import discord
import random
from discord.ext import commands
import aiohttp
import asyncio


class UtilCommandsCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
	
	@commands.command()
	@commands.guild_only()
	async def joined(self, ctx, *, member: discord.Member):

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

		member = ctx.author
		requested_by = "Requested by {}".format(ctx.author.name)
		latency = '{0}'.format(round(self.bot.latency, 1))
		desc = "{} ms".format(latency)

		embed = discord.Embed(title="", description="", colour=member.colour)
		embed.set_author(icon_url=self.bot.user.avatar_url, name=str(self.bot.user.name))
		embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/439905517280690176.png")
		embed.add_field(name="Latency:", value=desc, inline=False)
		embed.set_footer(text=requested_by)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def spotify(self, ctx, member: discord.Member):

		requested_by = "Requested by {}".format(ctx.author.name)
		listener = "{} is listening to:".format(member.name)
		spotify = member.activity
		duration = str(spotify.duration).split(".")[0]
		artists = str(spotify.artist).replace(";",",")

		embed = discord.Embed(title="", description="", colour=spotify.colour)
		embed.set_author(icon_url="https://images-eu.ssl-images-amazon.com/images/I/51rttY7a%2B9L.png", name=listener)
		embed.set_thumbnail(url=spotify.album_cover_url)
		embed.add_field(name="Title:", value=spotify.title, inline=False)
		embed.add_field(name="Artists:", value=artists, inline=False)
		embed.add_field(name="Album:", value=spotify.album, inline=False)
		embed.add_field(name="Duration:", value=duration, inline=False)
		embed.set_footer(text=requested_by)
		await ctx.send(embed=embed)


	@commands.command(name='createinvite',aliases=['createinv','create_inv','create_invite'])
	@commands.guild_only()
	async def createinvite(self, ctx):

		requested_by = "Requested by {}".format(ctx.author.name)
		channel = ctx.channel
		inv = await channel.create_invite(reason="Created via command")
		embed = discord.Embed(title="Invite Created", description=inv.url, color=ctx.author.colour)
		embed.set_thumbnail(url="https://twemoji.maxcdn.com/2/72x72/1f517.png")
		embed.set_footer(text=requested_by)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def roll(self, ctx, maximum_roll = 100):

		member = ctx.author
		rolled = random.randint(0,maximum_roll)

		embed = discord.Embed(title="", description="", colour=member.colour)
		embed.set_author(icon_url=member.avatar_url, name=str(member))
		embed.set_thumbnail(url="https://twemoji.maxcdn.com/2/72x72/1f3b2.png")
		embed.add_field(name="Rolled:", value=rolled, inline=True)
		embed.add_field(name="Roll Cap:", value=maximum_roll, inline=True)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def choose(self, ctx, *choices : str):

		member = ctx.author
		choice = random.choice(choices)

		embed = discord.Embed(title="", description="", colour=member.colour)
		embed.set_author(icon_url=member.avatar_url, name=str(member))
		embed.set_thumbnail(url="https://twemoji.maxcdn.com/2/72x72/1f3b2.png")
		embed.add_field(name="Chose:", value=choice, inline=True)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def cat(self, ctx):
		async with aiohttp.ClientSession() as session:
			async with session.get('http://aws.random.cat/meow') as r:
				if r.status == 200:

					js = await r.json()
					embed = discord.Embed(title=":cat: Random Cat", description="", colour=ctx.author.colour)
					embed.set_image(url=js['file'])
					requested_by = "Requested by {}".format(ctx.author.name)
					embed.set_footer(text=requested_by)
					await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def dog(self, ctx):
		async with aiohttp.ClientSession() as session:
			async with session.get('http://random.dog/woof.json') as r:
				if r.status == 200:
					js = await r.json()
					embed = discord.Embed(title=":dog: Random Dog", description="", colour=ctx.author.colour)
					embed.set_image(url=js['url'])
					requested_by = "Requested by {}".format(ctx.author.name)
					embed.set_footer(text=requested_by)
					await ctx.send(embed=embed)

@commands.command()
@commands.guild_only()
async def clock(self, ctx):

	botmsg = await ctx.send("Clocking..")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock1:")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock2:")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock3:")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock4:")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock5:")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock6:")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock7:")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock8:")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock9:")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock10:")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock11:")
	await asyncio.sleep(1)
	await botmsg.edit(content=":clock12:")
	await botmsg.add_reaction("🏁")


def setup(bot):
	bot.add_cog(UtilCommandsCog(bot))
