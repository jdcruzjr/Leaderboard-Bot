import sqlite3

def init_db():
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor
    c.execute('''Create statement goes here ''')
    conn.commit()
    conn.close

def add():
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    c.execute('insert statement goes here')
    conn.commit()
    conn.close
    
def get():
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    c.execute('query statement goes here')
    conn.commit()
    conn.close
    return "return variable goes here"