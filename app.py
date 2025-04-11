from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from src.controllers.controller import generatenewResume

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )



@app.post("/")
async def upload( nome: str = Form(...),
    file: UploadFile = File(...)
):
    text = await generatenewResume(nome, file)
    return text


@app.get("/")
async def root():
    return {"message": "Hello World"}