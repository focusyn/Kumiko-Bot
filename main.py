import discord
import os, random, asyncio, requests, json 
from discord.ext import commands, tasks
import key
from key import osukey 

client = commands.Bot(command_prefix = "o!")
client.remove_command('help')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(client.guilds)

@client.event
async def on_member_join(member):
	print(f'{member} has joined the server.')
	await ctx.send(f'{member} has joined the server.')

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    responses = ['yes.', 'no.', 'shut up', 'youre mom gay']
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')
    
@client.command(aliases=['say'])
async def _say(ctx, *, te):
    response = te
    await ctx.message.delete()
    await ctx.send(response)

# AMONG US RELATED COMMANDS: 

@client.command()
@commands.has_guild_permissions(mute_members=True)
async def vcmute(ctx):
    vc = ctx.author.voice.channel
    for member in vc.members:
        await member.edit(mute=True)
    
    
@client.command()
@commands.has_guild_permissions(mute_members=True)
async def vcunmute(ctx):
    vc = ctx.author.voice.channel
    for member in vc.members:
        await member.edit(mute=False)

# OSU! COMMANDS: 

def osuuser(username):
    url = f'https://osu.ppy.sh/api/get_user?k={osukey}&u={username}'
    response = requests.get(url, verify=True)
    data=response.json()
    embed = discord.Embed(
        colour=discord.Color.green(),
        title=(f'{data[0]["username"]}'),
        url=(f'https://osu.ppy.sh/users/{data[0]["user_id"]}')
    )
    embed.set_thumbnail(url=f'https://a.ppy.sh/{data[0]["user_id"]}')
    embed.add_field(name='Hit Accuracy', value=f'{data[0]["accuracy"][0:5]}%', inline=False)
    embed.add_field(name='Account Created on', value=f'{data[0]["join_date"]} UTC', inline=False)
    embed.add_field(name='Playcount', value=f'{data[0]["playcount"]}', inline=False)
    embed.add_field(name='Total PP', value=f'{data[0]["pp_raw"]}', inline=False)
    return embed

@client.command(brief="Get info on an osu user")
async def osu(ctx, *, username=None):
	if username==None:
		embed = discord.Embed(
			colour=discord.Color.red(),
			description="Please provide a Username"
		)
		await ctx.send(embed=embed)
	else:
		embed = osuuser(username)
		embed.set_footer(text=f'Requested by {ctx.author}')
		await ctx.send(embed=embed)


@client.command()
async def help(ctx):
	pages = 1
	cur_page = 1

	embed1=discord.Embed(color=ctx.author.color)
	embed1.set_author(name="Help",icon_url="https://clipartstation.com/wp-content/uploads/2018/09/clipart-question-mark-1-1.jpg")
	embed1.set_footer(text=f'Page 1/{pages} - Requested by {ctx.author}')
	embed1.add_field(name="help", value="Show this message",inline=False)
	embed1.add_field(name="vcmute",value="Mutes everyone in a voice channel.",inline=False)
	embed1.add_field(name="vcunmute", value="Unmutes everyone in a voice channel.",inline=False)
	embed1.add_field(name="8ball <Question>", value="Ask bot a question.",inline=False)
	embed1.add_field(name="ping", value="Check the bot's ping.",inline=False)
	embed1.add_field(name="say <text>", value="Make the bot say something",inline=False)
	
	contents = [ embed1 ]
	message = await ctx.send(embed=contents[cur_page-1])

	await message.add_reaction("◀️")
	await message.add_reaction("▶️")

	def check(reaction, user):
		return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

	while True:
		try:
			reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)

			if str(reaction.emoji) == "▶️" and cur_page != pages:
				cur_page += 1
				await message.edit(embed=contents[cur_page-1])
				await message.remove_reaction(reaction, user)

			elif str(reaction.emoji) == "◀️" and cur_page > 1:
				cur_page -= 1
				await message.edit(embed=contents[cur_page-1])
				await message.remove_reaction(reaction, user)

			else:
				await message.remove_reaction(reaction, user)
		except asyncio.TimeoutError:
			await message.delete()
			break

client.run(key.botkey)
