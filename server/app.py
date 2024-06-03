import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from openai import OpenAI

app = FastAPI()

# OpenAI Start
client = OpenAI(api_key='')

# Initialize the database
#############################################
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS cards (id INTEGER PRIMARY KEY, title TEXT, description TEXT, html TEXT, tags TEXT, author TEXT, created_at TEXT, edit_password TEXT)')
conn.commit()
conn.close()
#############################################

path_to_htmls = 'htmls/'

## These are Routes for HTMLs that are Static
# For / serve home.html
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open(path_to_htmls + 'home.html', 'r') as file:
        html = file.read()
    return HTMLResponse(content=html)

# For /cards serve cards.html
@app.get("/cards", response_class=HTMLResponse)
def read_cards():
    with open(path_to_htmls + 'cards.html', 'r') as file:
        html = file.read()
    return HTMLResponse(content=html)

# For /new serve new.html
@app.get("/new", response_class=HTMLResponse)
def read_new():
    with open(path_to_htmls + 'new.html', 'r') as file:
        html = file.read()
    return HTMLResponse(content=html)

# For /edit serve edit.html
'''
@app.get("/edit", response_class=HTMLResponse)
def read_edit():
    with open(path_to_htmls + 'edit.html', 'r') as file:
        html = file.read()
    return HTMLResponse(content=html)
'''

# For /card/{id} find in database, return whole entry, and let me edit it
@app.get("/card/{id}", response_class=HTMLResponse)
def read_card(id: int):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM cards WHERE id=?', (id,))
    card = c.fetchone()
    conn.close()
    if card:
        html = f'''
        <html>
            <head>
                <title>{card[1]}</title>
            </head>
            <body>
                <h1>{card[1]}</h1>
                <p>{card[2]}</p>
                <p> By: {card[5]}</p>
                <button id="share">Share</button>
                <div>
                    {card[3]}
                </div>
                <script>
                    document.getElementById('share').addEventListener('click', () => {{
                        navigator.share({{
                            title: '{card[1]}',
                            text: '{card[2]}',
                            url: window.location.href
                        }})
                    }})
                </script>
            </body>
        </html>
        '''
        return HTMLResponse(content=html)
    else:
        return HTMLResponse(content='Card not found')

# Route for saving a new card
@app.post("/publish")
def create_card(title: str, description: str, html: str, tags: str, author: str, edit_password: str):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO cards (title, description, html, tags, author, created_at, edit_password) VALUES (?, ?, ?, ?, ?, datetime("now"), ?)', (title, description, html, tags, author, edit_password))
    conn.commit()
    card_id = c.lastrowid
    conn.close()
    return {'id': card_id}

# Route for openai command post json input request
@app.post("/api/command")
async def create_command(request: Request):
    data = await request.json()
    command = data['command']
    present_state = data['presentState']
    sys_prompt = "You are HyperCardGPT, an AI programmer who receives HTML for a self contained DIV and a command that directs what to add to the HTML of the DIV. Do not include boilerplate-- this is for inside a DIV, so format stuff appropriately. Your job is to interpret the command, and modify the HTML in such a way so as to add what the command asks for. Add all stylings inside the DIV and also all scripts. Make sure that whatever you add fits inside the div and does not overrun in. You are to return HTML only. No comments, no extra text. Just the HTML, since it will be rendered in a browser."
    user_prompt = f"The present state of the HTML is: {present_state}. The command you are to interpret is: {command}. Please return the HTML in full after you have made the necessary modifications. Only the HTML, no comments, no extra text. It will be rendered in a browser. Keep in mind that this will go inside a div in an existing HTML file."
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    response = completion.choices[0].message.content
    print(response)
    return {'html': response}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
