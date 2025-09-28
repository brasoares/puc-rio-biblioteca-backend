from flask import Blueprint, jsonify, request
from app import db
from models.livro import Livro
from flasgger import swag_from

livros_bp = Blueprint('livros', __name__)

@livros_bp.route('/livros', methods=['GET'])
@swag_from({
    'tags': ['Livros'],
    'summary': 'Lista todos os livros com filtros opcionais',
    'parameters': [
        {
            'name': 'genero',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filtrar por gênero'
        },
        {
            'name': 'disponivel',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Filtrar apenas disponíveis'
        },
        {
            'name': 'idade_recomendada',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filtrar por idade recomendada'
        },
        {
            'name': 'classicos',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Filtrar apenas clássicos da família'
        }
    ],
    'responses': {
        200: {'description': 'Lista de livros retornada com sucesso'}
    }
})
def listar_livros():
    try:
        query = Livro.query
        
        # Filtros opcionais
        genero = request.args.get('genero')
        if genero:
            query = query.filter_by(genero=genero)
        
        disponivel = request.args.get('disponivel')
        if disponivel and disponivel.lower() == 'true':
            query = query.filter_by(disponivel=True)
        
        idade = request.args.get('idade_recomendada')
        if idade:
            query = query.filter_by(idade_recomendada=idade)
        
        classicos = request.args.get('classicos')
        if classicos and classicos.lower() == 'true':
            query = query.filter_by(classicos_familia=True)
        
        livros = query.all()
        return jsonify([l.to_dict() for l in livros]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@livros_bp.route('/livros/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['Livros'],
    'summary': 'Busca um livro por ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do livro'
        }
    ],
    'responses': {
        200: {'description': 'Livro encontrado'},
        404: {'description': 'Livro não encontrado'}
    }
})
def buscar_livro(id):
    livro = Livro.query.get(id)
    if livro:
        return jsonify(livro.to_dict()), 200
    return jsonify({'erro': 'Livro não encontrado'}), 404

@livros_bp.route('/livros', methods=['POST'])
@swag_from({
    'tags': ['Livros'],
    'summary': 'Cadastra um novo livro',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['titulo', 'autor'],
                'properties': {
                    'isbn': {'type': 'string'},
                    'titulo': {'type': 'string'},
                    'autor': {'type': 'string'},
                    'editora': {'type': 'string'},
                    'ano_publicacao': {'type': 'integer'},
                    'genero': {'type': 'string'},
                    'subgenero': {'type': 'string'},
                    'idioma': {'type': 'string'},
                    'num_paginas': {'type': 'integer'},
                    'idade_recomendada': {'type': 'string'},
                    'localizacao': {'type': 'string'},
                    'estado_conservacao': {'type': 'string'},
                    'capa_url': {'type': 'string'},
                    'sinopse': {'type': 'string'},
                    'origem': {'type': 'string'},
                    'valor_estimado': {'type': 'number'},
                    'classicos_familia': {'type': 'boolean'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Livro criado com sucesso'},
        400: {'description': 'Dados inválidos'},
        409: {'description': 'ISBN já cadastrado'}
    }
})
def criar_livro():
    try:
        data = request.get_json()
        
        if not data.get('titulo') or not data.get('autor'):
            return jsonify({'erro': 'Título e autor são obrigatórios'}), 400
        
        # Verifica ISBN duplicado
        if data.get('isbn'):
            if Livro.query.filter_by(isbn=data['isbn']).first():
                return jsonify({'erro': 'ISBN já cadastrado'}), 409
        
        novo_livro = Livro(
            isbn=data.get('isbn'),
            titulo=data['titulo'],
            autor=data['autor'],
            editora=data.get('editora'),
            ano_publicacao=data.get('ano_publicacao'),
            genero=data.get('genero'),
            subgenero=data.get('subgenero'),
            idioma=data.get('idioma', 'Português'),
            num_paginas=data.get('num_paginas'),
            idade_recomendada=data.get('idade_recomendada', 'Todas'),
            localizacao=data.get('localizacao'),
            estado_conservacao=data.get('estado_conservacao', 'Bom'),
            capa_url=data.get('capa_url'),
            sinopse=data.get('sinopse'),
            origem=data.get('origem'),
            valor_estimado=data.get('valor_estimado'),
            classicos_familia=data.get('classicos_familia', False)
        )
        
        db.session.add(novo_livro)
        db.session.commit()
        
        return jsonify(novo_livro.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@livros_bp.route('/livros/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['Livros'],
    'summary': 'Atualiza informações de um livro',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do livro'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'titulo': {'type': 'string'},
                    'autor': {'type': 'string'},
                    'editora': {'type': 'string'},
                    'ano_publicacao': {'type': 'integer'},
                    'genero': {'type': 'string'},
                    'subgenero': {'type': 'string'},
                    'idioma': {'type': 'string'},
                    'num_paginas': {'type': 'integer'},
                    'idade_recomendada': {'type': 'string'},
                    'localizacao': {'type': 'string'},
                    'estado_conservacao': {'type': 'string'},
                    'capa_url': {'type': 'string'},
                    'sinopse': {'type': 'string'},
                    'origem': {'type': 'string'},
                    'valor_estimado': {'type': 'number'},
                    'classicos_familia': {'type': 'boolean'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Livro atualizado com sucesso'},
        404: {'description': 'Livro não encontrado'}
    }
})
def atualizar_livro(id):
    try:
        livro = Livro.query.get(id)
        if not livro:
            return jsonify({'erro': 'Livro não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualiza campos permitidos
        campos_atualizaveis = ['titulo', 'autor', 'editora', 'ano_publicacao', 
                               'genero', 'subgenero', 'idioma', 'num_paginas',
                               'idade_recomendada', 'localizacao', 'estado_conservacao',
                               'capa_url', 'sinopse', 'origem', 'valor_estimado',
                               'classicos_familia']
        
        for campo in campos_atualizaveis:
            if campo in data:
                setattr(livro, campo, data[campo])
        
        db.session.commit()
        return jsonify(livro.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@livros_bp.route('/livros/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['Livros'],
    'summary': 'Remove um livro do catálogo',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do livro'
        }
    ],
    'responses': {
        200: {'description': 'Livro removido com sucesso'},
        400: {'description': 'Livro está emprestado'},
        404: {'description': 'Livro não encontrado'}
    }
})
def deletar_livro(id):
    try:
        livro = Livro.query.get(id)
        if not livro:
            return jsonify({'erro': 'Livro não encontrado'}), 404
        
        if not livro.disponivel:
            return jsonify({'erro': 'Não é possível remover um livro emprestado'}), 400
        
        db.session.delete(livro)
        db.session.commit()
        
        return jsonify({'mensagem': 'Livro removido com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500