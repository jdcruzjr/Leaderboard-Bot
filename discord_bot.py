import discord
import os 
from dotenv import load_dotenv
from discord.ext import commands
import leaderboard
import podium_generator
import database as db 

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
client = discord.Client(intents=intents)
token = os.getenv('token')
client = commands.Bot(command_prefix="!")



@client.event
async def on_ready():
    # Creates Global tables
    db.init_db()
    print("I'm a chungus")
    db.load_db()
    
@client.event
async def on_message(message):
    username = str(message.author).split("#")[0]
    channel = str(message.channel.name)
    user_message = str(message.content)
    
    print(f"Hello Chungus {username}, {user_message}, in channel {channel}")
    
    if message.author == client.user:
        return
    
    if channel == "general":
        if user_message.lower() == "hello":
            await message.channel.send(f"Hello big chungus {message.author.mention}")
            
@client.command
async def add_points(ctx, arg):
      await ctx.send('Added Points to User')
            

            
client.run(token)