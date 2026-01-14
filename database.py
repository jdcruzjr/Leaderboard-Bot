import sqlite3
import sqlite3

def init_db():
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")

    # USERS table
    c.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        discord_id CHAR(20),
        CONSTRAINT users_pk PRIMARY KEY (discord_id)
    );
    """)

    # SERVERS table
    c.execute("""
    CREATE TABLE IF NOT EXISTS Servers (
        guild_id INT,
        guild_name CHAR(100),
        CONSTRAINT servers_pk PRIMARY KEY (guild_id)
    );
    """)

    # GAMES table (auto increment)
    c.execute("""
    CREATE TABLE IF NOT EXISTS Games (
        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name CHAR(100) UNIQUE
    );
    """)

    # ServerUsers table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ServerUsers (
        discord_id CHAR(20),
        guild_id INT,
        CONSTRAINT serverusers_pk PRIMARY KEY (discord_id, guild_id),
        CONSTRAINT serverusers_fk_1 FOREIGN KEY (discord_id)
            REFERENCES USERS(discord_id)
            ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT serverusers_fk_2 FOREIGN KEY (guild_id)
            REFERENCES SERVERS(guild_id)
            ON DELETE CASCADE ON UPDATE CASCADE
    );
    """)

    # ServerGames table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ServerGames (
        game_id INT,
        guild_id INT,
        CONSTRAINT servergames_pk PRIMARY KEY (game_id, guild_id),
        CONSTRAINT servergames_fk_1 FOREIGN KEY (guild_id)
            REFERENCES SERVERS(guild_id)
            ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT servergames_fk_2 FOREIGN KEY (game_id)
            REFERENCES GAMES(game_id)
            ON DELETE CASCADE ON UPDATE CASCADE
    );
    """)

    # Scores table
    c.execute("""
    CREATE TABLE IF NOT EXISTS Scores (
        discord_id CHAR(20),
        game_id INT,
        guild_id INT,
        points DOUBLE,
        CONSTRAINT scores_pk PRIMARY KEY (discord_id, game_id, guild_id),
        CONSTRAINT scores_fk_1 FOREIGN KEY (guild_id)
            REFERENCES SERVERS(guild_id)
            ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT scores_fk_2 FOREIGN KEY (game_id)
            REFERENCES GAMES(game_id)
            ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT scores_fk_3 FOREIGN KEY (discord_id)
            REFERENCES USERS(discord_id)
            ON DELETE CASCADE ON UPDATE CASCADE
    );
    """)

    conn.commit()
    conn.close()


def add_game(guild_id, server_name, game_name):
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")

    # Insert server if missing
    c.execute("INSERT OR IGNORE INTO SERVERS (guild_id, guild_name) VALUES (?, ?);", 
              (guild_id, server_name))

    # Insert game if missing
    c.execute("INSERT OR IGNORE INTO GAMES (game_name) VALUES (?);", 
              (game_name,))

    # Get the game_id for the game_name
    c.execute("SELECT game_id FROM GAMES WHERE game_name = ?;", (game_name,))
    game_id = c.fetchone()[0]

    # Link server and game
    c.execute("INSERT OR IGNORE INTO ServerGames (guild_id, game_id) VALUES (?, ?);",
              (guild_id, game_id))

    conn.commit()
    conn.close()

def remove_game(guild_id, game_name):
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    # Find Game ID
    c.execute("SELECT game_id FROM GAMES WHERE game_name = ?;", (game_name,))
    game_id = c.fetchone()[0]
    
    # Delete Game
    c.execute("DELETE FROM ServerGames WHERE guild_id = ? AND game_id = ?;", (guild_id, game_id))
    conn.commit()
    conn.close()
    
def add_points(guild_id, discord_tag, game_name, points):
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    
    # Ensure the user exists globally
    c.execute("INSERT OR IGNORE INTO USERS (discord_tag) VALUES (?);", (discord_tag, ))
    
    # Ensure the user is a member of this server
    c.execute("INSERT OR IGNORE INTO ServerUsers (discord_tag, guild_id) VALUES (?, ?);", (discord_tag, guild_id))
    
    c.execute("SELECT game_id FROM GAMES WHERE game_name = ?;", (game_name,))
    game_id = c.fetchone()[0]
    
    # Ensure a score row exists for (user, game, server)
    # Start at 0 if this is their first time playing 
    c.execute("INSERT OR IGNORE INTO Scores (discord_tag, game_id, guild_id, points) VALUES (?, ?, ?, 0);", (discord_tag, game_id, guild_id))
    
    # Add Points to user
    c.execute("UPDATE SCORES SET points = points + ? where discord_tag = ? and game_id = ? and guild_id = ?;", (points, discord_tag, game_id, guild_id))
    
    conn.commit()
    conn.close()
    
def remove_points(points, guild_id, discord_tag, game_name):
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    
    c.execute("SELECT game_id FROM GAMES WHERE game_name = ?;", (game_name,))
    game_id = c.fetchone()[0]
    
    # Remove points
    c.execute("UPDATE SCORES SET points = points - ? where discord_tag = ? and game_id = ? and guild_id = ?;", (points, discord_tag, game_id, guild_id))
    conn.commit()
    conn.close()
    
# Retreive the scores of players in server for a specific game    
def load_leaderboard_instance(guild_id, game_name):
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    c.execute('SELECT discord_tag, points FROM Scores INNER JOIN Games on Games.game_id == Scores.game_id where Scores.guild_id == ? and game_name == ?', (guild_id, game_name))
    scores = c.fetchall()
    conn.commit()
    conn.close()
    return scores

# Get existing games in a server
def get_games_of_server(guild_id):
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    c.execute('SELECT game_name FROM ServerGames INNER JOIN Games on Games.game_id == ServerGames.game_id where Scores.guild_id == ?', (guild_id, ))
    games = c.fetchall()
    conn.commit()
    conn.close()
    return games
