from itertools import count
from typing import Optional
from flask import Flask, request, jsonify
from flask_pydantic_spec import (
        FlaskPydanticSpec, Response, Request
        )
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


server =  Flask(__name__)
spec = FlaskPydanticSpec('flask', title='Dev Júnior...')
spec.register(server)
database = TinyDB(storage=MemoryStorage)
c = count()

class QueryPessoa(BaseModel):
    id: Optional[int]
    nome: Optional[str]
    idade: Optional[int]


class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(c))
    nome: str
    idade: int


class Pessoas(BaseModel):
    pessoas: list[Pessoa]
    count: int

@server.get('/pessoas')
@spec.validate(
        query=QueryPessoa,
        resp=Response(HTTP_200=Pessoas))
def buscar_pessoas():
    '''
    buscar_pessoas: Localiza todas as Pessoas no banco de dados
    '''
    query = request.context.query.dict(exclude_none=True)
    # breakpoint()
    todas_as_pessoas = database.search(
            Query().fragment(query)
            )
    return jsonify(
            Pessoas(
                pessoas = todas_as_pessoas,
                count = len(todas_as_pessoas)
            ).dict()
    )


@server.get('/pessoa/<int:id>')
@spec.validate(resp=Response(HTTP_200=Pessoa))
def buscar_pessoa(id):
    '''
    buscar_pessoa: Localiza uma Pessoa no banco de dados
    '''
    try:
        pessoa = database.search(Query().id == id)[0]
    except IndexError:
        return {'message': 'Pessoa not found'}, 404
    return jsonify(pessoa)

@server.post('/pessoas')
@spec.validate(
        body=Request(Pessoa), resp=Response(HTTP_200=Pessoa)
        )
def inserir_pessoas():
    '''
    inserir_pessoas: Insere uma Pessoa no banco de dados
    '''
    body = request.context.body.dict()
    database.insert(body)
    return body


@server.put('/pessoas/<int:id>')
@spec.validate(
        body=Request(Pessoa), resp=Response(HTTP_200=Pessoa)
        )
def altera_pessoa(id):
    '''
    altera_pessoa: Atualiza informações de uma Pessoa no banco de dados
    '''
    Pessoa = Query()
    body = request.context.body.dict()
    database.update(body, Pessoa.id == id)
    return jsonify(body)


@server.delete('/pessoas/<int:id>')
@spec.validate(resp=Response('HTTP_204'))
def deleta_pessoa(id):
    '''
    deleta_pessoa: Remove uma Pessoa do banco de dados
    '''
    database.remove(Query().id == id)
    return jsonify({})


if __name__ == "__main__":
    server.run(debug=True)
