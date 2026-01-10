import discord
import os 
from dotenv import load_dotenv
from discord.ext import commands
import leaderboard
import podium_generator

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
client = discord.Client(intents=intents)
token = os.getenv('token')
client = commands.Bot(command_prefix="!")



@client.event
async def on_ready():
    print("I'm a chungus")
    
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
            

            
client.run(token)