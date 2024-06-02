import sqlite3
from fastapi import FastAPI
import openai

app = FastAPI()

# Initialize the database 
#############################################
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS cards (id INTEGER PRIMARY KEY, title TEXT, description TEXT, html TEXT), tags TEXT, author TEXT, created_at TEXT, edit_password TEXT')
conn.commit()
conn.close()
#############################################

path_to_htmls = 'htmls/'

## These are Routes for HTMLs that are Static
# For / serve home.html
@app.get("/")
def read_root():
    with open(path_to_htmls + 'home.html', 'r') as file:
        html = file.read()
    return html

# For /cards serve cards.html
@app.get("/cards")
def read_cards():
    with open(path_to_htmls + 'cards.html', 'r') as file:
        html = file.read()
    return html

# For /new serve new.html
@app.get("/new")
def read_new():
    with open(path_to_htmls + 'new.html', 'r') as file:
        html = file.read()
    return html

# For /edit serve edit.html
@app.get("/edit")
def read_edit():
    with open(path_to_htmls + 'edit.html', 'r') as file:
        html = file.read()
    return html

# For /card/{id} find in database, read the html field and return it
@app.get("/card/{id}")
def read_card(id: int):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT html FROM cards WHERE id = ?', (id,))
    html = c.fetchone()[0]
    conn.close()
    return html

