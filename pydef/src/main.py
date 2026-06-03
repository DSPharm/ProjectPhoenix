from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def home():
    return{"mesaj": "Salut din FastAPI!"}

@app.get("/casa")
def home():
    return{"mesaj": "Salut din CASA!"}

@app.get("/Buna", response_class=HTMLResponse)
def home():
    return """
        <html>
            <body>
            <h1>Buna Iubire!</h1>
            </body>
        </html>
        """