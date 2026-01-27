from email.mime import image
import discord
from discord import Embed
import os 
from dotenv import load_dotenv
from discord.ext import commands
import leaderboard
import podium_generator
import database as db 
import podium_generator as pg

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
async def add_points(ctx, member: discord.Member, game:str, points: int):
    guild_id = ctx.guild.id
    curr_lb = leaderboard_maps[guild_id][game]
    
    if curr_lb:
        db.add_points(guild_id, member.name, game, points)
        curr_lb.increase_points(member.name, points)
        await ctx.send('Added Points to User')
    else:
        await ctx.send('Game leaderboard doesn\'t exist')


@add_points.error
async def add_points_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("I couldn’t find that member! Please mention a valid user.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument! Make sure you provide points as a number or the game name.")
            
@client.command
async def remove_points(ctx, member: discord.Member, game:str, points: int):
    guild_id = ctx.guild.id
    
    curr_lb = leaderboard_maps[guild_id][game]
    if curr_lb:
        db.remove_points_points(guild_id, member.name, game, int)
        curr_lb.decrease_points(member.name, points)
        await ctx.send('Added Points to User')
    else:
        await ctx.send('Game leaderboard doesn\'t exist')
    
    
@remove_points.error
async def remove_points_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("I couldn’t find that member! Please mention a valid user.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument! Make sure you provide points as a number or the game name.")

@client.command
async def create_game(ctx, game:str):
    guild_id = ctx.guild.id
    guild_name = ctx.guild.name
    
    games_list = db.get_games_of_server(guild_id)
    
    if leaderboard_maps[guild_id][game] or (game,) in games_list:
        await ctx.send('Game leaderboard already exists')
    else:
        db.add_game(guild_id,guild_name,game)
        leaderboard_maps[guild_id][game] = leaderboard.Leaderboard(game)
        
@create_game.error
async def create_game_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument! Make sure you provide a game")
        
@client.command
async def delete_game(ctx, game:str):
    guild_id = ctx.guild.id
    guild_name = ctx.guild.name
    
    games_list = db.get_games_of_server(guild_id)
    
    if not leaderboard_maps[guild_id][game] or (game,) not in games_list:
        await ctx.send('Game leaderboard doesn\'t exists')
    else:
        db.remove_game(guild_id,guild_name,game)
        leaderboard_maps[guild_id].pop(game, None)

@delete_game.error
async def delete_game_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument! Make sure you provide a game")
          
@client.command
async def add_player(ctx, member: discord.Member, game_name: str):
    guild_id = ctx.guild.id
    player = db.get_player_in_game(guild_id, member.name, game_name)

    if player is None:
        
        curr_lb = leaderboard_maps[guild_id][game_name]
        if curr_lb:
            db.add_points(guild_id, member.name, game_name, 0)
            curr_lb.add_player(member.name)
            await ctx.send('Added Player to Game')
        else:
            await ctx.send('Game leaderboard doesn\'t exist')
        
    else:
        await ctx.send("Player already exists in the game")

@add_player.error
async def add_player_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("I couldn’t find that member! Please mention a valid user.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument! Make sure you provide the proper values.")

@client.command
async def remove_player(ctx, member: discord.Member, game_name: str):
    guild_id = ctx.guild.id
    player = db.get_player_in_game(guild_id, member.name, game_name)

    if player is None:
        await ctx.send("Player doesn't exist in the game")    

    else:
        curr_lb = leaderboard_maps[guild_id][game_name]
        if curr_lb:
            db.remove_player(guild_id, member.name, game_name)
            curr_lb.remove(member.name)
            await ctx.send('Removed player from the game')

@remove_player.error
async def remove_player_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("I couldn’t find that member! Please mention a valid user.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument! Make sure you provide the proper values.")

@client.command
async def reset_players(ctx, game_name):
    guild_id = ctx.guild.id
    if db.get_game(game_name):
        db.reset_all_points_in_game(guild_id, game_name)
        curr_lb = leaderboard_maps[guild_id][game_name]
        curr_lb.reset_all_players()
        
    else:
        await ctx.send("Game doesn't exist")
        
@reset_players.error
async def reset_players_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument! Make sure you provide the proper values.")


@client.command
async def show_players(ctx, game_name):
    guild_id = ctx.guild.id
    
    lb = leaderboard_maps[guild_id][game_name]
    
    if not lb:
        await ctx.send('Game leaderboard doesn\'t exists')
    else:
        
        players_list = db.get_player_list_in_game(guild_id, game_name)
        player_names = [name_tuple[0] for name_tuple in players_list]
        
        
        # member name -> member object for guild
        member_lookup = {
            member.name: member
            for member in ctx.guild.members
        }

        # member name -> member object for game in guild
        member_objects =  {
            name: member_lookup.get(name)
            for name in player_names
            if name in member_lookup
        }   
        
        image_bytes = pg.generate_podium_image(lb, member_objects, "podium.png")
        
        lb_names = lb.get_list_of_players_ordered()
        file = discord.File(fp=image_bytes, filename="podium.png")
        title_lb = f"{game_name} Leaderboard"
        
        if len(lb_names) > 3:
            lb_names = lb_names[2:]
            names_str_list = "\n".join(lb_names)

            embed = Embed(
                title=title_lb,
                description=names_str_list,
                color=0x3498db
            )
        else:
            embed = Embed(
                title=title_lb,
                color=0x3498db
            )

        embed.set_image(url="attachment://podium.png")
        await ctx.send(embed=embed, file=file)

client.run(token)
