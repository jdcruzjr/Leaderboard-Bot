import discord
import os 
from dotenv import load_dotenv
from discord.ext import commands
import leaderboard
import podium_generator
import database as db 

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True 

load_dotenv()
client = discord.Client(intents=intents)
token = os.getenv('token')
client = commands.Bot(command_prefix="!")

# Server - > { Game -> Leaderboard instance } 
leaderboard_maps = {}

@client.event
async def on_ready():
    # Creates Global tables
    db.init_db()
    print("I'm a chungus")
    
    for guild in client.guilds:
        
        if guild.guild_id not in leaderboard_maps:
            leaderboard_maps[guild.guild_id] = {}
        
        game_list = db.get_games_of_server(guild.guild_id)
        # If server has games in db to load
        if game_list:
            
            #For each game in server
            for game in game_list:
                # Make a leaderboard instance for that game
                temp_lb = leaderboard.Leaderboard(game)
                
                # Get discord tags and points associated with the game
                scores = db.load_leaderboard_instance(guild.guild_id, game)
                
                # Add to heap
                temp_lb.load_heap(scores)
                
                # Add to map
                leaderboard_maps[guild.guild_id][game] = temp_lb
    
    
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