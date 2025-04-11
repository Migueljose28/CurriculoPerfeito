from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette import status
from pydantic import BaseModel
import httpx  # biblioteca para fazer requisições HTTP
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch



app = FastAPI()

class base(BaseModel):
    curriculo: str


# Carrega o modelo e o tokenizer uma única vez
tokenizer = T5Tokenizer.from_pretrained("unicamp-dl/ptt5-base-portuguese-vocab")
model = T5ForConditionalGeneration.from_pretrained("unicamp-dl/ptt5-base-portuguese-vocab")

def melhorar_texto_para_curriculo(texto: str) -> str:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    entrada = f"Reescreva o texto de forma profissional para um currículo: {texto}"

    inputs = tokenizer.encode(entrada, return_tensors="pt", max_length=512, truncation=True).to(device)
    outputs = model.generate(inputs, max_new_tokens=200, num_beams=4, early_stopping=True)

    resposta = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return resposta



async def corrigir_com_languagetool(texto):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.languagetool.org/v2/check",
            data={
                "text": texto,
                "language": "pt-BR"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        result = response.json()

        # Aplica correções
        corrigido = texto
        for match in reversed(result.get("matches", [])):
            start = match["offset"]
            end = start + match["length"]
            if match["replacements"]:
                replacement = match["replacements"][0]["value"]
                corrigido = corrigido[:start] + replacement + corrigido[end:]

        return corrigido

@app.post("/curriculo", status_code=status.HTTP_201_CREATED)
async def enviar_curriculo(curriculo: base):
    texto_corrigido = await corrigir_com_languagetool(curriculo.curriculo)
    texto_corrigido = melhorar_texto_para_curriculo(texto_corrigido)
    imagem_path = None

    return JSONResponse(content={
        "mensagem": "Currículo processado com sucesso!",
        "curriculo_corrigido": texto_corrigido,
        "imagem_salva": imagem_path if imagem_path else "Nenhuma imagem enviada"
    })



# Carrega o modelo de reescrita ou parafraseamento
rephrase = pipeline("text2text-generation", model="Vamsi/T5_Paraphrase_Paws")

class TextoRequest(BaseModel):
    texto: str

@app.post("/reescrever-texto")
async def reescrever_texto(request: TextoRequest):
    try:
        texto = request.texto
     
        entrada = f"paraphrase: {texto} </s>"
        saida = rephrase(entrada, max_length=100, num_return_sequences=1, do_sample=True)
        return {"texto_reescrito": saida[0]['generated_text']}
    except Exception as e:
        return {"error": str(e)}
    