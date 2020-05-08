import discord
from discord.ext import commands
import random
import asyncio
import logging

log = logging.getLogger(__name__)

class Minigames(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.guild_only()
	async def race(self, ctx):
		"""Does a random lap time with a car"""
		animations = [
		"<:raceflags:433061672387739650> :wavy_dash::wavy_dash::wavy_dash::wavy_dash::wavy_dash: <:Audi:433020256521551893>",
		"<:raceflags:433061672387739650> :wavy_dash::wavy_dash::wavy_dash::wavy_dash: <:Audi:433020256521551893>",
		"<:raceflags:433061672387739650> :wavy_dash::wavy_dash::wavy_dash: <:Audi:433020256521551893>",
		"<:raceflags:433061672387739650> :wavy_dash::wavy_dash: <:Audi:433020256521551893>",
		"<:raceflags:433061672387739650> :wavy_dash: <:Audi:433020256521551893>",
		"<:raceflags:433061672387739650> <:Audi:433020256521551893>"
		]
		car_speed_by_step = []
		total_car_speed_by_step = 0

		member = ctx.author
		total_time = 0

		embed = discord.Embed(
		title="",
		description="",
		colour=member.colour)
		embed.set_author(
		icon_url=member.avatar_url,
		name=f"{member.name}'s car")

		game_object = await ctx.send(embed=embed)

		for animation_speed in animations:
			car_speed_by_step.append(random.randint(1,10))
		for speed_by_step in car_speed_by_step:
			total_car_speed_by_step += speed_by_step

		i = 0
		for next_animation in animations:
			embed.description = next_animation
			await game_object.edit(embed=embed)
			await asyncio.sleep(car_speed_by_step[i])
			total_time += car_speed_by_step[i]
			i += 1

		await asyncio.sleep(1)

		embed.description = ""
		embed.set_thumbnail(url="https://twemoji.maxcdn.com/2/72x72/23f1.png")
		embed.add_field(name="Lap Time:", value=f'{total_time} seconds', inline=False)
		embed.add_field(name="Distance:", value=f'600 meters', inline=False)
		embed.add_field(name="Average Speed:", value=f'{int((600/total_car_speed_by_step)*3.6)} Km/h', inline=False)

		await game_object.edit(embed=embed)

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
