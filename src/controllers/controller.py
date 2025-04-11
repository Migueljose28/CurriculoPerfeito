
from fastapi import FastAPI, File, UploadFile, Form
import fitz  # PyMuPDF
import re

def limpar_texto(texto: str) -> str:
    texto = texto.replace('\ufeff', '')
    texto = re.sub(r'\n+', '\n', texto) 
    texto = re.sub(r'[ ]{2,}', ' ', texto)  
    texto = texto.strip() 
    return texto;


async def generatenewResume(nome: str, file: UploadFile):
    textFile = await TransformerPdfIntext(file);
    textFomate = limpar_texto(textFile)
    return {"textfile": textFomate, "nome": nome}



async def TransformerPdfIntext(file: UploadFile = File(...)):
    conteudo = await file.read()      
    doc = fitz.open(stream=conteudo, filetype="pdf")
    texto_extraido = ""

    for pagina in doc:
        texto_extraido += pagina.get_text()

    return texto_extraido

