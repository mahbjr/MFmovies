from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from http import HTTPStatus
import csv
from pathlib import Path
import hashlib
import zipfile

app = FastAPI()
CSV_FILE = "filmes.csv"

class Filme(BaseModel):
    titulo: str
    diretor: str
    ano_lancamento: int
    sinopse: str
    duracao: int  # em minutos

filmes: List[Filme] = []

# Função para carregar filmes do CSV
def carregar_filmes_csv():
    if Path(CSV_FILE).exists():
        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            filmes = []
            for row in reader:
                filme = Filme(
                        titulo=row["titulo"],
                        diretor=row["diretor"],
                        ano_lancamento=int(row["ano_lancamento"]),
                        sinopse=row["sinopse"],
                        duracao=int(row["duracao"])
                    )
                filmes.append(filme)
            return filmes
    return []

# f1
def salvar_filmes_csv():
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["titulo", "diretor", "ano_lancamento", "sinopse", "duracao"])
        writer.writeheader()
        for filme in filmes:
            writer.writerow(filme.model_dump())

filmes = carregar_filmes_csv()

@app.get("/")
def read_root():
    return {"msg": "Bem-vindo à MFmovies!"}

#f2
@app.get("/filmes/", response_model=List[Filme])
def listar_filmes():
    filmes = carregar_filmes_csv()
    return filmes

#f3
@app.get("/filmes/{titulo}", response_model=Filme)
def obter_filme(titulo: str):
    filmes = carregar_filmes_csv()
    for filme in filmes:
        if filme.titulo == titulo:
            return filme
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Filme não encontrado.")

#f1 f3
@app.post("/filmes/", response_model=Filme, status_code=HTTPStatus.CREATED)
def adicionar_filme(filme: Filme):
    for f in filmes:
        if f.titulo == filme.titulo:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Filme com este título já existe.")
    filmes.append(filme)
    salvar_filmes_csv()
    return filme

#f3
@app.put("/filmes/{titulo}", response_model=Filme)
def atualizar_filme(titulo: str, filme_atualizado: Filme):
    filmes = carregar_filmes_csv()
    for indice, filme_atual in enumerate(filmes):
        if filme_atual.titulo == titulo:
            filmes[indice] = filme_atualizado
            salvar_filmes_csv()
            return filme_atualizado
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Filme não encontrado.")

@app.delete("/filmes/{titulo}")
def remover_filme(titulo: str):
    filmes = carregar_filmes_csv()
    for filme in filmes:
        if filme.titulo == titulo:
            filmes.remove(filme)
            salvar_filmes_csv()
            return {"msg": "Filme removido com sucesso."}
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Filme não encontrado.")

#f4
@app.get("/contar")
def contar_filmes():
    filmes = carregar_filmes_csv()
    return {"quantidade": len(filmes)}

#f5
@app.get("/compactar")
def compactar_csv():
    if not Path(CSV_FILE).exists():
        raise HTTPException(status_code=404, detail="Arquivo CSV não encontrado.")
    zip_filename = CSV_FILE.replace(".csv", ".zip")
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        zipf.write(CSV_FILE)
    return {"msg": "Arquivo compactado como " + zip_filename}

#f6
@app.get("/hash")
def calcular_hash_csv():
    if not Path(CSV_FILE).exists():
        raise HTTPException(status_code=404, detail="Arquivo CSV não encontrado.")
    with open(CSV_FILE, mode="rb") as file:
        conteudo = file.read()
    sha256_hash = hashlib.sha256(conteudo).hexdigest()
    return {"hash": sha256_hash}