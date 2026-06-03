from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return{"mesaj": "Salut din FastAPI!"}

@app.get("/casa")
def home():
    return{"mesaj": "Salut din CASA!"}