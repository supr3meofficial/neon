import discord
from discord.ext import commands
import random
import asyncio
import logging

log = logging.getLogger(__name__)

async def track_animation(trackracer, ctx):

	anim = ["<:raceflags:433061672387739650> :wavy_dash::wavy_dash::wavy_dash::wavy_dash::wavy_dash: <:Audi:433020256521551893>",
	"<:raceflags:433061672387739650> :wavy_dash::wavy_dash::wavy_dash::wavy_dash: <:Audi:433020256521551893>",
	"<:raceflags:433061672387739650> :wavy_dash::wavy_dash::wavy_dash: <:Audi:433020256521551893>",
	"<:raceflags:433061672387739650> :wavy_dash::wavy_dash: <:Audi:433020256521551893>",
	"<:raceflags:433061672387739650> :wavy_dash: <:Audi:433020256521551893>",
	"<:raceflags:433061672387739650> <:Audi:433020256521551893>"]

	def tracksleeper():
		return random.randint(1,10)

	member = ctx.author
	membercar = "{}'s car".format(member.name)
	totaltracksleep = 0

	for step in anim:
		embed = discord.Embed(title="", description=step, colour=member.colour)
		embed.set_author(icon_url=member.avatar_url, name=membercar)
		trackmsg = await ctx.send(embed=embed)
		tracksleep = tracksleeper()
		await asyncio.sleep(tracksleep)
		totaltracksleep += tracksleep

	await asyncio.sleep(1)
	laptime = "{} seconds".format(totaltracksleep)
	embed = discord.Embed(title="", description="", colour=member.colour)
	embed.set_author(icon_url=member.avatar_url, name=membercar)
	embed.set_thumbnail(url="https://twemoji.maxcdn.com/2/72x72/23f1.png")
	embed.add_field(name="Lap Time:", value=laptime, inline=False)
	await trackmsg.edit(embed=embed)

class Minigames(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.guild_only()
	async def race(self, ctx):
		"""Does a random lap time with a car"""
		await track_animation(ctx.author.mention, ctx)

	@commands.command(name='hide')
	@commands.guild_only()
	async def hide(self, ctx):
		"""Reacts to a random old message (last 30). Click the reaction to win!"""
		channel = ctx.channel
		author = ctx.author

		m = await channel.send("Hiding!")
		await asyncio.sleep(2)
		await m.delete()

		messages = await channel.history(limit=30).flatten()
		message_set = random.choice(messages)
		message = message_set

		await message.add_reaction("<:Neon:665702985799565317>")
		m2 = await channel.send("<:Neon:665702985799565317> You have 15 seconds to find me!")

		try:
			reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=lambda reaction,user: user == author and str(reaction.emoji) == '<:Neon:665702985799565317>' and reaction.message.id == message.id)
		except asyncio.TimeoutError:
			await m2.delete()
			await channel.send('<:Neon:665702985799565317> Game over! Better luck next time')
		else:
			await m2.delete()
			await channel.send('<:Neon:665702985799565317> You found me!')

def setup(bot):
	bot.add_cog(Minigames(bot))
