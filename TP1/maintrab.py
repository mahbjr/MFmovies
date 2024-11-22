from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from http import HTTPStatus
import csv
from pathlib import Path
import hashlib
import zipfile

app = FastAPI()
CSV_FILE = "filmes.csv"

# Modelo Pydantic para Filme
class Filme(BaseModel):
    titulo: str
    diretor: str
    ano_lancamento: int
    sinopse: str
    duracao: int  # em minutos

# Inicializando a lista de filmes na memória
filmes: List[Filme] = []

# Helper para carregar filmes do CSV
def carregar_filmes_csv():
    if Path(CSV_FILE).exists():
        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return [Filme(**row) for row in reader]
    return []

# Helper para salvar filmes no CSV
def salvar_filmes_csv():
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["titulo", "diretor", "ano_lancamento", "sinopse", "duracao"])
        writer.writeheader()
        for filme in filmes:
            writer.writerow(filme.dict())

# Inicializa a lista de filmes
filmes = carregar_filmes_csv()

@app.get("/")
def read_root():
    return {"msg": "Bem-vindo à API de Filmes!"}

#f2
@app.get("/filmes/", response_model=List[Filme])
def listar_filmes():
    return filmes

#f3
@app.get("/filmes/{titulo}", response_model=Filme)
def obter_filme(titulo: str):
    for filme in filmes:
        if filme.titulo == titulo:
            return filme
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Filme não encontrado.")

#f1 f3
@app.post("/filmes/", response_model=Filme, status_code=HTTPStatus.CREATED)
def adicionar_filme(filme: Filme):
    if any(f.titulo == filme.titulo for f in filmes):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Filme com este título já existe.")
    filmes.append(filme)
    salvar_filmes_csv()
    return filme

#f3
@app.put("/filmes/{titulo}", response_model=Filme)
def atualizar_filme(titulo: str, filme_atualizado: Filme):
    for indice, filme_atual in enumerate(filmes):
        if filme_atual.titulo == titulo:
            filmes[indice] = filme_atualizado
            salvar_filmes_csv()
            return filme_atualizado
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Filme não encontrado.")

@app.delete("/filmes/{titulo}")
def remover_filme(titulo: str):
    for filme in filmes:
        if filme.titulo == titulo:
            filmes.remove(filme)
            salvar_filmes_csv()
            return {"msg": "Filme removido com sucesso."}
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Filme não encontrado.")

#f4
@app.get("/filmes/count")
def contar_filmes():
    return {"quantidade": len(filmes)}

#f5
@app.get("/filmes/compactar")
def compactar_csv():
    zip_filename = CSV_FILE.replace(".csv", ".zip")
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        zipf.write(CSV_FILE)
    return {"msg": "Arquivo compactado como " + zip_filename}

#f6
@app.get("/filmes/hash")
def calcular_hash_csv():
    sha256_hash = hashlib.sha256()
    with open(CSV_FILE, mode="rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return {"hash": sha256_hash.hexdigest()}