import discord
from discord.ext import commands
import random
import logging

log = logging.getLogger(__name__)

class Fun(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.guild_only()
	async def onedeag(self, ctx, member: discord.Member = None):
		"""Pops a one-deag on someone"""
		if member is None:
			member = random.choice(ctx.guild.members)

		deags = ["https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_gs_deagle_aggressor_light_large.51ffb87f03ae0d3c467d4412f3c246067748e61d.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_am_scales_bravo_light_large.6cba46695e74a8bee932ea90cea24e146cbef5e7.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_gs_deagle_mecha_light_large.e08c1fd8709f6b368956c41c68b17c15ff635635.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_aq_deserteagle_kumichodragon_light_large.19874e9a20cfac49efbe1f1557b995e453633ffe.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_cu_deagle_aureus_light_large.7fa76057cb05f2cab829be448f120ae540715d0e.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_am_ddpatdense_peacock_light_large.a486db3160bcdcf6bc5a1d8179c450b02f620151.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_aa_vertigo_light_large.85a16e4bfb8b1cc6393ca5d0c6d3a1e6e6023323.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_gs_deagle_exo_light_large.8bdc93f1b45efba187748065deff967eef8f2f2d.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_aq_desert_eagle_constable_light_large.fb2f2673dd3997a21bff9129e0d2e294c03095e8.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_aq_deagle_naga_light_large.b410ad835b1894a448676ae0590586298af2cb33.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_hy_webs_darker_light_large.7b9cb19bac52ebe7c49e3abdfb0c400ea252fef8.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_aq_engraved_deagle_light_large.804a1a01a29bf80673b739f3eb220272a6838193.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_am_seastorm_shojo_light_large.7df4fe386dac18ae2a8c3e50df7dfb9165dece83.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_am_seastorm_blood_light_large.1e92a7e19fde014e5a70832a93b440e0c036d596.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_aq_handcannon_light_large.e6e87ceb2337a423d225dc177342af3df4069585.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_aq_pilot_deagle_light_large.60b0e755ef14311a82f5f35928ad18dbb6ae2a86.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_aa_flames_light_large.dd140c3b359c16ccd8e918ca6ad0b2628151fe1c.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_cu_desert_eagle_corroden_light_large.5fde2cc1c9b82b0e9823445c7fb2be334bc286af.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_aq_deagle_corinthian_light_large.1a694892a1953a131775451d0542508b4b3d9e77.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_am_bronze_sparkle_light_large.42dc1d2bae9e586f75d6425f94a195014891533b.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_am_crystallized_dark_light_large.2d7d753a893ec3f0a470af9690aa64dcecd7146f.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_hy_varicamo_urban_light_large.a9791d0046206f88085f2d0850ec577c6f535a47.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_so_night_light_large.64e315553578f3c8bd08c96622fc2c34d5a789ba.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_am_seastorm_light_large.aef21efecda37237d24debe3f409f42954dadddd.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_hy_ddpat_urb_light_large.06af0cb0e08490f1fba17acd1b9c98978745c213.png",
				"https://steamcdn-a.akamaihd.net/apps/730/icons/econ/default_generated/weapon_deagle_hy_mottled_sand_light_large.615be084d4bc9db8c98451f13351cae1fa0ec69c.png",
				"https://csgostash.com/img/weapons/Desert_Eagle.png"]

		deag = random.choice(deags)
		embed = discord.Embed(title="", description="", color=ctx.author.color)
		embed.set_author(icon_url=member.avatar_url, name=member.name)
		embed.set_thumbnail(url=deag)
		embed.add_field(name="You have popped a one deag on:", value=member.name, inline=True)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def dab(self, ctx, member = "everyone"):
		"""Dabs on the haters."""
		msg = "<:Dab:443893837388316673> {} just dabbed on {}".format(ctx.author.name, member)
		embed = discord.Embed(title="<:Dab:443893837388316673> Dabbing on the haters", description=msg, colour=ctx.author.colour)
		embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/443893837388316673.png")
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def mitochondria(self, ctx):
		"""Tell ISIS the mitochondria is the powerhouse of the cell"""
		embed = discord.Embed(title="Mitochondria", description="", colour=ctx.author.colour)
		embed.set_image(url="https://i.imgur.com/80iINul.jpg")
		requested_by = "Requested by {}".format(ctx.author.name)
		embed.set_footer(text=requested_by)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def literallyme(self, ctx):
		"""Literally me"""
		literallyme = ["https://i.imgur.com/J56l01s.jpg","https://i.imgur.com/BE1Roa6.jpg","https://i.imgur.com/EOn4t0v.jpg","https://i.imgur.com/GOmd9sE.jpg","https://i.imgur.com/b4RCKxD.jpg","https://i.imgur.com/u45VL8K.jpg","https://i.imgur.com/b9Z1f0H.png","https://cdn.discordapp.com/attachments/390888617536651265/441616070302760960/17493891_1009834615783993_1976996299869782016_n.jpg","https://cdn.discordapp.com/attachments/367744546752430082/442416104611250177/20180505_195713.JPG"]
		embed = discord.Embed(title="Literally me", description="", colour=ctx.author.colour)
		embed.set_image(url=random.choice(literallyme))
		requested_by = "Requested by {}".format(ctx.author.name)
		embed.set_footer(text=requested_by)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def nani(self, ctx, member: discord.Member = None):
		"""Nani!?"""
		author = ctx.message.author
		members = ctx.guild.members

		if member == None:
			member = random.choice(members)
		embed = discord.Embed(title="", description="Omae wa mou shindeiru!")
		embed.set_author(icon_url=author.avatar_url, name=author.name)
		await ctx.send(embed=embed)
		embed = discord.Embed(title="", description="Nani!?")
		embed.set_author(icon_url=member.avatar_url, name=member.name)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def cat(self, ctx):
		"""Posts a random cat picture"""
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
	async def dog(self, ctx):
		"""Posts a random dog picture"""
		async with aiohttp.ClientSession() as session:
			async with session.get('http://random.dog/woof.json') as r:
				if r.status == 200:
					js = await r.json()
					embed = discord.Embed(title=":dog: Random Dog", description="", colour=ctx.author.colour)
					embed.set_image(url=js['url'])
					requested_by = "Requested by {}".format(ctx.author.name)
					embed.set_footer(text=requested_by)
					await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Fun(bot))
