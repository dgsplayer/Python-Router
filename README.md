OR-Tools em Python para roterização de entregas

## Observações Douglas
Python deve ser 64 bits por causa do ortools
python -m pip install --upgrade pip
psycopg2 não funciona na versão python 3.7


## Arquivos principais

run.py - Arquivo inicial para ser rodado no python

router/ - Pasta contendo o código fonte para roterização

database.sql - Script de criação de tabela 

teste.json - JSON de exemplo para roterização

## Endpoint

*/health*

Responde 200 - OK caso o Python esteja rodando

*/router*

Endpoint para realizar a roteirização.
Metodo HTTP: POST
JSON de exemplo: vide arquivo *teste.json*


## Variaveis de ambiente

Quando uma roterização ocorre com sucesso, os dados são gravadas na tabela ortools do Postgres.
Os dados de conexão são encontrados através das seguintes variaveis:
(Os dados a direita são apenas para exemplo)

DB_HOSTNAME = localhost
DB_PORT = 32768
DB_DB = postgres
DB_USER = postgres
DB_PWD = ortools


## Para rodar local

Bibliotecas requeridas:

- `Postgres`
- `Python +3.6`
- `pip`


### Passo a passo

*(Os comandos a seguir de python3 e pip podem variar de máquina a máquina)*

Instale as dependencias via pip
`python3 -m pip install -U --user -r requirements.txt`

Export as variaveis de ambiente com os dados correto de conexão ao postgres

Rode o arquivo run.py

`python3 run.py`

O output que deve aparecer no LOG é:

```
 * Serving Flask app "router.app" (lazy loading)
 * Environment: prod
 * Debug mode: off
 * Running on http://0.0.0.0:8080
```

A aplicação sobe na porta 8080, caso precise alterar, edite o arquivo run.py


## Ambiente de Produção

Crie uma imagem com base no Dockerfile que se encontra no repositório

`docker build --tag=ortoolsv2 .`

Rode a imagem, expondo a porta 8080 e informando as variaveis de ambiente:

` docker run -p 8080:8080 --network host -e DB_HOSTNAME=172.17.0.1 -e DB_PORT=32768 -e DB_USER=postgres -e DB_DB=postgres -e DB_PWD=ortools ortoolsv2`
