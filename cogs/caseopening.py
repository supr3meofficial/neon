import discord
from discord.ext import commands
import random
import asyncio
import aiohttp
import urllib.request
import os

class CaseOpeningCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1, 8, commands.BucketType.user)
	async def opencase(self, ctx, opencase_set='default'):

			member = ctx.author

			#Case Opening Items

			case_items = [
			"★ M9 Bayonet | Doppler",			#0
			"★ Karambit | Doppler",				#1
			"AK-47 | Bloodsport",           	#2
			"M4A1-S | Decimator",           	#3
			"AWP | Oni Taji",               	#4
			"AWP | Hyper Beast",            	#5
			"USP-S | Torque",               	#6
			"AUG | Ricochet",               	#7
			"Galil AR | Rocket Pop",        	#8
			"MAG-7 | Sonar",               		#9
			"UMP-45 | Riot",                	#10
			"M4A1-S | Flashback",           	#11
			"Desert Eagle | Crimson Web",   	#12
			"Desert Eagle | Kumicho Dragon", 	#13
			"AK-47 | Case Hardened",        	#14
			"Bayonet | Case Hardened",      	#15
			"Bowie Knife | Tiger Tooth",    	#16
			"★ Bloodhound Gloves | Snakebite", 	#17
			"PP-Bizon | Osiris",            	#18
			"M4A4 | Evil Daimyo",           	#19
			"Galil AR | Crimson Tsunami",   	#20
			"P250 | Wingshot",              	#21
			"Glock-18 | Bunsen Burner",			#22
			"P2000 | Pulse",                	#23
			"AK-47 | Elite Build",          	#24
			"MP7 | Armor Core",             	#25
			"MP7 | Urban Hazard",           	#26
			"Five-SeveN | Urban Hazard",    	#27
			"Sawed-Off | Origam",          		#28
			"M249 | System Lock",           	#29
			"Negev | Terrain",              	#30
			"★ M9 Bayonet | Autotronic",      	#31
			"★ Shadow Daggers | Slaughter",   	#32
			"★ Flip Knife | Crimson Web",     	#33
			"AWP | Asiimov",					#34
			"★ Driver Gloves | Convoy",			#35
			"AK-47 | Fire Serpent",         	#36
			"Desert Eagle | Golden Koi",    	#37
			"M4A1-S | Bright Water",        	#38
			"USP-S | Orion",                	#39
			"M4A1-S | Atomic Alloy",        	#40
			"SCAR-20 | Cyrex",              	#41
			"CZ75-Auto | Twist",            	#42
			"P2000 | Oceanic",              	#43
			"Glock-18 | Off World",         	#44
			"UMP-45 | Metal Flowers",       	#45
			"Tec-9 | Cut Out",              	#46
			"M4A4 | Neo-Noir",              	#47
			"MP7 | Bloodsport",             	#48
			"AWP | Mortis",                		#49
			"USP-S | Cortex",               	#50
			"AUG | Stymphalian",            	#51
			"Glock-18 | Moonrise",          	#52
			"UMP-45 | Arctic Wolf",         	#53
			"MAG-7 | SWAG-7",               	#54
			"Negev | Lionfish",             	#55
			"Nova | Wild Six",              	#56
			"R8 Revolver | Grip",           	#57
			"P2000 | Urban Hazard",         	#58
			"Five-SeveN | Flame Test",      	#59
			"SG 553 | Aloha",               	#60
			"MP9 | Black Sand",             	#61
			"PP-Bizon | Night Riot",        	#62
			"XM1014 | Oxide Blaze",         	#63
			"★ Hydra Gloves | Case Hardened", 	#64
			"★ Hydra Gloves | Emerald",       	#65
			"★ Hydra Gloves | Rattle",       	#66
			"★ Hydra Gloves | Mangrovef",      	#67
			"★ Specialist Gloves | Foundation", #68
			"★ Specialist Gloves | Crimson Web",#69
			"★ Specialist Gloves | Mogul",    	#70
			"★ Specialist Gloves | Buckshot", 	#71
			"★ Sport Gloves | Omega",         	#72
			"★ Sport Gloves | Vice",          	#73
			"★ Sport Gloves | Amphibious",    	#74
			"★ Sport Gloves | Bronze Morph",  	#75
			"★ Hand Wraps | Cobalt Skulls",   	#76
			"★ Hand Wraps | Overprint",       	#77
			"★ Hand Wraps | Duct Tape",       	#78
			"★ Hand Wraps | Arboreal",        	#79
			"★ Moto Gloves | POW!",           	#80
			"★ Moto Gloves | Turtle ",         	#81
			"★ Moto Gloves | Transport",      	#82
			"★ Moto Gloves | Polygon",        	#83
			"★ Driver Gloves | King Snake",   	#84
			"★ Driver Gloves | Imperial Plaid",	#85
			"★ Driver Gloves | Overtake",     	#86
			"★ Driver Gloves | Racing Green",  	#87
			"M4A4 | Faded Zebra",				#88
			"CZ75-Auto | Polymer",				#89
			"CZ75-Auto | Imprint",				#90
			"Galil AR | Black Sand",			#91
			"Galil AR | Kami",					#92
			"SSG 08 | Necropos",				#93
			"SSG 08 | Abyss",					#94
			"SG 553 | Ultraviolet",				#95
			"R8 Revolver | Crimson Web",		#96
			"USP-S | Blueprint",				#97
			"USP-S | Night Ops",				#98
			"Desert Eagle | Oxide Blaze",		#99
			"P250 | Whiteout",					#100
			"R8 Revolver | Survivalist",		#101
			"Dual Berettas | Shred",			#102
			"AUG | Amber Slipstream",			#103
			"MP9 | Capillary",					#104
			"Tec-9 | Snek-9",					#105
			"P90 | Traction",					#106
			"Glock-18 | Warhawk",				#107
			"Nova | Toy Soldier",				#108
			"G3SG1 | High Seas",				#109
			"MP7 | Powercore",					#110
			"CZ75-Auto | Eco",					#111
			"AWP | PAW",						#112
			"Sawed-Off | Devourer",				#113
			"FAMAS | Eye of Athena",			#114
			"M4A1-S | Nightmare",				#115
			"Desert Eagle | Code Red",			#116
			"AK-47 | Neon Rider",				#117
			"Nova | Wood Fired", 				#118
			"Sawed-Off | Black Sand", 			#119
			"MP9 | Modest Threat", 				#120
			"SG 553 | Danger Close", 			#121
			"Glock-18 | Oxide Blaze", 			#122
			"M4A4 | Magnesium", 				#123
			"Tec-9 | Fubar", 					#124
			"G3SG1 | Scavenger", 				#125
			"Galil AR | Signal", 				#126
			"MAC-10 | Pipe Down:", 				#127
			"P250 | Nevermore", 				#128
			"USP-S | Flashback", 				#129
			"UMP-45 | Momentum", 				#130
			"Desert Eagle | Mecha Industries", 	#131
			"MP5-SD | Phosphor", 				#132
			"AWP | Neo-Noir", 					#133
			"AK-47 | Asiimov", 					#134
			"MP7 | Mischief", 					#135
			"FAMAS | Crypsis", 					#136
			"Galil AR | Akoben", 				#137
			"P250 | Verdigris", 				#138
			"MAC-10 | Whitefish", 				#139
			"P90 | Off World", 					#140
			"AK-47 | Uncharted", 				#141
			"Tec-9 | Bamboozle", 				#142
			"UMP-45 | Moonrise", 				#143
			"MP5-SD | Gauss", 					#144
			"Desert Eagle | Light Rail",		#145
			"AWP | Atheris", 					#146
			"R8 Revolver | Skull Crusher", 		#147
			"AUG | Momentum", 					#148
			"XM1014 | Incinegator", 			#149
			"Five-SeveN | Angry Mob",			#150
			"M4A4 | Emperor",					#151
			"★ Navaja Knife | Fade", 			#152
			"★ Stilleto Knife | Rust Coat", 	#153
			"★ Talon Knife | Blue Steel", 		#154
			"★ Ursus Knife | Tiger Tooth", 		#155
			"AWP | Wildfire", 					#156
			"FAMAS | Commemoration", 			#157
			"MP9 | Hydra", 						#158
			"AUG | Death by Puppy", 			#159
			"P90 | Nostalgia", 					#160
			"MP5-SD | Agent", 					#161
			"UMP-45 | Plastique", 				#162
			"P250 | Inferno", 					#163
			"M249 | Aztec", 					#164
			"Five-SeveN | Buddy", 				#165
			"Glock-18 | Sacrifice", 			#166
			"FAMAS | Decommissioned", 			#167
			"Dual Berettas | Elite 1.6", 		#168
			"MAC-10 | Classic Crate.", 			#169
			"MAG-7 | Popdog", 					#170
			"Tec-9 | Flash Out", 				#171
			"SCAR-20 | Assault", 				#172
			"★ Classic Knife", 			   		#173
			"★ Classic Knife | Slaughter", 	    #174
			"★ Classic Knife | Fade", 			#175
			"★ Classic Knife | Crimson Web", 	#176
			"AWP | Containment Breach", 		#177
			"MAC-10 | Stalker", 				#178
			"SG 553 | Colony IV",				#179
			"SSG 08 | Bloodshot", 				#180
			"Tec-9 | Decimator", 				#181
			"AK-47 | Rat Rod", 					#182
			"AUG | Arctic Wolf",				#183
			"P2000 | Obsidian", 				#184
			"MP7 | Neon Ply", 					#185
			"PP-Bizon | Embargo", 				#186
			"R8 Revolver | Memento", 			#187
			"Dual Berettas | Balance",			#188
			"MP5-SD | Acid Wash", 				#189
			"SCAR-20 | Torn",					#190
			"Nova | Plume", 					#191
			"M249 | Warbird", 					#192
			"G3SG1 | Black Sand", 				#193
			"★ Nomad Knife | Stained", 			#194
			"★ Skeleton Knife ", 				#195
			"★ Survival Knife | Case Hardened", #196
			"★ Paracord Knife | Blue Steel",	#197
			"Glock-18 | Bullet Queen",			#198
			"M4A1-S | Player Two",				#199
			"AK-47 | Phantom Disruptor",		#200
			"MAC-10 | Disco Tech",				#201
			"MAG-7 | Justice",					#202
			"SG 553 | Darkwing",				#203
			"Sawed-Off | Apocalypto",			#204
			"SCAR-20 | Enforcer",				#205
			"SSG 08 | Fever Dream",				#206
			"P2000 | Acid Etched",				#207
			"Desert Eagle | Blue Ply",			#208
			"AWP | Capillary",					#209
			"R8 Revolver | Bone Forged",		#210
			"AUG | Tom Cat",					#211
			"MP5-SD | Desert Strike",			#212
			"Negev | Prototype",				#213
			"CZ75-Auto | Distressed"			#214
			]

			csgo_pins = [
			"Civil Protection Pin",
			"Alyx Pin",
			"Howl Pin",
			"Brigadier General Pin",
			"Valeria Phoenix Pin",
			"Chroma Pin",
			"Guardian Elite Pin",
			"Dust II Pin",
			"Sustenance! Pin",
			"Vortigaunt Pin",
			"Aces High Pin",
			"Hydra Pin",
			"Cache Pin",
			"Bloodhound Pin",
			"Mirage Pin",
			"Inferno Pin",
			"Copper Lambda Pin",
			"Health Pin",
			"Headcrab Glyph Pin",
			"Wildfire Pin",
			"Easy Peasy Pin",
			"Inferno 2 Pin",
			"Office Pin",
			"Cobblestone Pin",
			"Overpass Pin",
			"Victory Pin",
			"Italy Pin",
			"Militia Pin",
			"Lambda Pin",
			"Combine Helmet Pin",
			"Black Mesa Pin",
			"CMB Pin",
			"City 17 Pin",
			"Welcome to the Clutch Pin",
			"Death Sentence Pin",
			"Guardian 3 Pin",
			"Canals Pin",
			"Phoenix Pin",
			"Guardian 2 Pin",
			"Bravo Pin",
			"Baggage Pin",
			"Guardian Pin",
			"Nuke Pin",
			"Tactics Pin",
			"Train Pin"
			]

			case_items_knives_and_gloves = [
			case_items[0],
			case_items[1],
			case_items[15],
			case_items[16],
			case_items[17],
			case_items[31],
			case_items[32],
			case_items[33],
			case_items[35],
			case_items[64],
			case_items[65],
			case_items[66],
			case_items[67],
			case_items[68],
			case_items[69],
			case_items[70],
			case_items[71],
			case_items[72],
			case_items[73],
			case_items[74],
			case_items[75],
			case_items[76],
			case_items[77],
			case_items[78],
			case_items[79],
			case_items[80],
			case_items[81],
			case_items[82],
			case_items[83],
			case_items[84],
			case_items[85],
			case_items[86],
			case_items[87],
			case_items[152],
			case_items[153],
			case_items[154],
			case_items[155],
			case_items[173],
			case_items[174],
			case_items[175],
			case_items[176],
			case_items[194],
			case_items[195],
			case_items[196],
			case_items[197]
			]

			case_items_covert = [
			case_items[2],
			case_items[4],
			case_items[5],
			case_items[34],
			case_items[36],
			case_items[37],
			case_items[47],
			case_items[116],
			case_items[117],
			case_items[133],
			case_items[150],
			case_items[151],
			case_items[156],
			case_items[157],
			case_items[177],
			case_items[178],
			case_items[198],
			case_items[199]
			]

			case_items_classified = [
			case_items[3],
			case_items[13],
			case_items[14],
			case_items[38],
			case_items[39],
			case_items[40],
			case_items[48],
			case_items[49],
			case_items[50],
			case_items[113],
			case_items[114],
			case_items[115],
			case_items[130],
			case_items[131],
			case_items[132],
			case_items[147],
			case_items[148],
			case_items[149],
			case_items[158],
			case_items[159],
			case_items[160],
			case_items[179],
			case_items[180],
			case_items[181],
			case_items[200],
			case_items[201],
			case_items[202]
			]

			case_items_restricted = [
			case_items[11],
			case_items[12],
			case_items[18],
			case_items[19],
			case_items[20],
			case_items[21],
			case_items[38],
			case_items[51],
			case_items[52],
			case_items[53],
			case_items[54],
			case_items[55],
			case_items[108],
			case_items[109],
			case_items[110],
			case_items[111],
			case_items[112],
			case_items[125],
			case_items[126],
			case_items[127],
			case_items[128],
			case_items[129],
			case_items[141],
			case_items[142],
			case_items[143],
			case_items[144],
			case_items[145],
			case_items[146],
			case_items[161],
			case_items[162],
			case_items[163],
			case_items[164],
			case_items[165],
			case_items[182],
			case_items[183],
			case_items[184],
			case_items[185],
			case_items[186],
			case_items[203],
			case_items[204],
			case_items[205],
			case_items[206],
			case_items[207]
			]

			case_items_milspec = [
			case_items[6],
			case_items[7],
			case_items[8],
			case_items[9],
			case_items[10],
			case_items[22],
			case_items[23],
			case_items[24],
			case_items[25],
			case_items[26],
			case_items[27],
			case_items[28],
			case_items[29],
			case_items[30],
			case_items[41],
			case_items[42],
			case_items[43],
			case_items[44],
			case_items[45],
			case_items[46],
			case_items[56],
			case_items[57],
			case_items[58],
			case_items[59],
			case_items[60],
			case_items[61],
			case_items[62],
			case_items[63],
			case_items[63],
			case_items[88],
			case_items[89],
			case_items[90],
			case_items[91],
			case_items[92],
			case_items[93],
			case_items[94],
			case_items[95],
			case_items[96],
			case_items[97],
			case_items[98],
			case_items[99],
			case_items[100],
			case_items[101],
			case_items[102],
			case_items[103],
			case_items[104],
			case_items[105],
			case_items[106],
			case_items[107],
			case_items[118],
			case_items[119],
			case_items[120],
			case_items[121],
			case_items[122],
			case_items[123],
			case_items[124],
			case_items[135],
			case_items[136],
			case_items[137],
			case_items[138],
			case_items[139],
			case_items[140],
			case_items[141],
			case_items[166],
			case_items[167],
			case_items[168],
			case_items[169],
			case_items[170],
			case_items[171],
			case_items[172],
			case_items[187],
			case_items[188],
			case_items[189],
			case_items[190],
			case_items[191],
			case_items[192],
			case_items[193],
			case_items[208],
			case_items[209],
			case_items[210],
			case_items[211],
			case_items[212],
			case_items[213],
			case_items[214]
			]

			case_items_condition = [
			"Factory New",
			"Minimal Wear",
			"Field-Tested",
			"Well-Worn",
			"Battle-Scarred"
			]

			# - Case Opening Menu - #

			case_opening_showmenu=discord.Embed(
			title="",
			description=
			"""
**Select your preferred opening and click the matching reaction:**

<:csgocase:433064927645925386> Open skin case
<:csgopin:671062353948835850> Open pin capsule
""",
#<:csgotrophy:671062599617609728> Random trophy

			colour=0xc7c7c7)
			case_opening_showmenu.set_author(icon_url=self.bot.user.avatar_url, name='Neon Case Opening')
			case_opening_showmenu_obj = await ctx.send(embed=case_opening_showmenu)

			await case_opening_showmenu_obj.add_reaction('<:csgocase:433064927645925386>')
			#await case_opening_showmenu_obj.add_reaction('<:csgotrophy:671062599617609728>')
			await case_opening_showmenu_obj.add_reaction('<:csgopin:671062353948835850>')

			def check(reaction, user):

				return user == ctx.author and str(reaction.emoji) in [
				'<:csgocase:433064927645925386>',
				'<:csgotrophy:671062599617609728>',
				'<:csgopin:671062353948835850>'
				]

			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
				case_opening_showmenu_obj_reaction = str(reaction.emoji)
			except asyncio.TimeoutError:
				pass
			else:
				if case_opening_showmenu_obj_reaction == "<:csgocase:433064927645925386>":
					opencase_set = 'default'
				#elif case_opening_showmenu_obj_reaction == "<:csgotrophy:671062599617609728>":
				#	opencase_set = 'trophy'
				elif case_opening_showmenu_obj_reaction == "<:csgopin:671062353948835850>":
					opencase_set = 'pin'
				else:
					if ctx.author.id == 203299786382639104:
						pass
					else:
						opencase_set = 'default'

			# - StatTrak™ - #

			case_drop_statrak = random.randint(0,10)
			if case_drop_statrak == 10: stattrak = "StatTrak™ "
			else: stattrak = ""

			# - Drop Quality and Condition - #

			random_drop = random.randint(0,100)

			if random_drop <= 1: #Knives & Gloves - 1% Chance

				tier = "knife_gloves"
				stattrak = ""
				case_drop = random.choice(case_items_knives_and_gloves)
				case_drop_skinwear = case_items_condition[0]

			elif random_drop <= 6: #Covert - 5% Chance

				tier = "covert"
				case_drop = random.choice(case_items_covert)
				case_drop_skinwear =  random.choice(case_items_condition)

			elif random_drop <= 17: #Classified - 11% Chance

				tier = "classified"
				case_drop = random.choice(case_items_classified)
				case_drop_skinwear =  random.choice(case_items_condition)

			elif random_drop <= 37: #Restricted - 20% Chance

				tier = "restricted"
				case_drop = random.choice(case_items_restricted)
				case_drop_skinwear =  random.choice(case_items_condition)

			else: #Mil-Spec - 63% Chance

				tier = "milspec"
				case_drop = random.choice(case_items_milspec)
				case_drop_skinwear =  random.choice(case_items_condition)


			# - Case Opening Set - #

			if opencase_set == "default":

				opened_item = f"{stattrak}{case_drop} ({case_drop_skinwear})"

			elif opencase_set == "trophy":

				tier = "trophy"
				case_drop = random.choice(major_medals)
				opened_item = f"{case_drop} Trophy"

			elif opencase_set == "pin":

				tier = "pin"
				csgo_pins.append("Chroma Pin")
				case_drop = random.choice(csgo_pins)
				opened_item = case_drop

			elif opencase_set == "0":

				tier = "knife_gloves"
				case_drop = random.choice(case_items_knives_and_gloves)
				opened_item = f"{stattrak}{case_drop} ({case_items_condition[0]})"

			elif opencase_set == "1":

				tier = "milspec"
				case_drop = random.choice(case_items_milspec)
				opened_item = f"{stattrak}{case_drop} ({case_drop_skinwear})"

			elif opencase_set == "2":

				tier = "restricted"
				case_drop = random.choice(case_items_restricted)
				opened_item = f"{stattrak}{case_drop} ({case_drop_skinwear})"

			elif opencase_set == "3":

				tier = "classified"
				case_drop = random.choice(case_items_classified)
				opened_item = f"{stattrak}{case_drop} ({case_drop_skinwear})"

			elif opencase_set == "4":

				tier = "covert"
				case_drop = random.choice(case_items_covert)
				opened_item = f"{stattrak}{case_drop} ({case_drop_skinwear})"

			# - Skin Tier and Embed Colour - #

			def tier_colour():

				if tier == "milspec":
					return discord.Colour(0x177cc7)
				elif tier == "restricted":
					return discord.Colour(0x872de0)
				elif tier == "classified":
					return discord.Colour(0xc917e0)
				elif tier == "covert":
					return discord.Colour(0xe7191b)
				elif tier == "knife_gloves":
					return discord.Colour(0xe7191b)
				elif tier == "pin":
					return discord.Colour(0xe0d029)
				elif tier == "trophy":
					return discord.Colour(0x71e4cb)

			# - Setting Item Image URL - #

			async def set_opened_item_image(item_set=opencase_set):

				global opened_item_image

				#item_png_filename = opened_item.replace("™","")
				#item_png_filename = item_png_filename.replace("|","")
				#item_png_filename = item_png_filename.replace(" ","_")

				#print(f'[DEBUG] PNG File Name: "{item_png_filename}"; Opened Item: "{opened_item}"')

				#if not os.path.exists('./_cache'):
				#	try:
				#		os.makedirs('./_cache')
				#	except OSError:
				#		pass
				#if not os.path.isfile(f'./_cache/{item_png_filename}.png'):

				async with aiohttp.ClientSession() as session:
					async with session.get('http://api.steamapis.com/image/items/730') as r:
						if r.status == 200:
							js = await r.json()
						try:
							_js = js[opened_item]
							#urllib.request.urlretrieve(_js, f"./_cache/{item_png_filename}.png")
							#print(f'[DEBUG] Image URL: {_js}')
							opened_item_image = _js
						except KeyError:
							for i in range(len(case_items_condition)):
									try:
										_js = js[f'{stattrak}{case_drop} ({case_drop_skinwear[i]})']
										#urllib.request.urlretrieve(_js, f"./_cache/{item_png_filename}.png")
										#print(f'[DEBUG] Image URL: {_js}')
										opened_item_image = _js
									except KeyError:
											continue
				#else:
				#	print(f'[DEBUG] Image Cached: {item_png_filename}.png')
				#
				#	opened_item_image = f'./_cache_/{item_png_filename}.png'

			await set_opened_item_image()
			#Case Opening Animation

			case_opening_loading = discord.Embed(title="", description="", colour=0xc7c7c7)
			case_opening_loading.set_author(icon_url='https://cdn.discordapp.com/emojis/670804857124421635.gif', name='Opening Case...')

			case_opening_showdrop_max = discord.Embed(title="", description="", colour=tier_colour())
			case_opening_showdrop_max.set_author(icon_url=member.avatar_url, name=str(member))
			case_opening_showdrop_max.add_field(name="You have received:", value=opened_item, inline=False)
			case_opening_showdrop_max.set_image(url=opened_item_image)

			case_opening_showdrop_min = discord.Embed(title="", description="", colour=tier_colour())
			case_opening_showdrop_min.set_author(icon_url=member.avatar_url, name=str(member))
			case_opening_showdrop_min.add_field(name="You have received:", value=opened_item, inline=False)
			case_opening_showdrop_min.set_thumbnail(url=opened_item_image)

			msg = case_opening_showmenu_obj
			try:
				await case_opening_showmenu_obj.clear_reactions()
			except discord.Forbidden:
				embed = discord.Embed(title="Missing permissions",
				description="I cannot clear reactions. Please contact this server's administrator",
				colour=0xbf0000)
				embed.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.name)
				await ctx.send(embed=embed)

			await msg.edit(content="", embed=case_opening_loading)
			await asyncio.sleep(3)
			await msg.edit(content="", embed=case_opening_showdrop_max)
			await asyncio.sleep(5)
			await msg.edit(content="", embed=case_opening_showdrop_min)

def setup(bot):
	bot.add_cog(CaseOpeningCog(bot))
