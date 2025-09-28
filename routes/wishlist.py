# =====================================
# routes/wishlist.py - COMPLETE FILE
# =====================================
from flask import Blueprint, jsonify, request
from app import db
from models.wishlist import Wishlist
from models.membro import Membro
from models.livro import Livro
from flasgger import swag_from

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/wishlist', methods=['POST'])
@swag_from({
    'tags': ['Lista de Desejos'],
    'summary': 'Adiciona um livro à lista de desejos',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['id_membro'],
                'properties': {
                    'id_membro': {'type': 'integer'},
                    'id_livro': {'type': 'integer', 'description': 'Para livro já cadastrado'},
                    'titulo_desejado': {'type': 'string', 'description': 'Para livro não cadastrado'},
                    'autor_desejado': {'type': 'string'},
                    'prioridade': {'type': 'string', 'enum': ['baixa', 'média', 'alta']},
                    'notas': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Item adicionado à lista de desejos'},
        400: {'description': 'Dados inválidos'},
        409: {'description': 'Item já existe na lista'}
    }
})
def adicionar_wishlist():
    try:
        data = request.get_json()
        
        if not data.get('id_membro'):
            return jsonify({'erro': 'ID do membro é obrigatório'}), 400
        
        # Precisa ter ou id_livro ou titulo_desejado
        if not data.get('id_livro') and not data.get('titulo_desejado'):
            return jsonify({'erro': 'Informe o ID do livro ou o título desejado'}), 400
        
        # Verifica se o membro existe
        membro = Membro.query.get(data['id_membro'])
        if not membro:
            return jsonify({'erro': 'Membro não encontrado'}), 404
        
        # Se for livro cadastrado, verifica duplicata
        if data.get('id_livro'):
            wishlist_existente = Wishlist.query.filter_by(
                id_membro=data['id_membro'],
                id_livro=data['id_livro']
            ).first()
            
            if wishlist_existente:
                return jsonify({'erro': 'Este livro já está na sua lista de desejos'}), 409
            
            # Verifica se o livro existe
            livro = Livro.query.get(data['id_livro'])
            if not livro:
                return jsonify({'erro': 'Livro não encontrado'}), 404
        
        # Se for livro não cadastrado, verifica duplicata por título
        elif data.get('titulo_desejado'):
            wishlist_existente = Wishlist.query.filter_by(
                id_membro=data['id_membro'],
                titulo_desejado=data['titulo_desejado']
            ).first()
            
            if wishlist_existente:
                return jsonify({'erro': 'Este título já está na sua lista de desejos'}), 409
        
        novo_item = Wishlist(
            id_membro=data['id_membro'],
            id_livro=data.get('id_livro'),
            titulo_desejado=data.get('titulo_desejado'),
            autor_desejado=data.get('autor_desejado'),
            prioridade=data.get('prioridade', 'média'),
            notas=data.get('notas')
        )
        
        db.session.add(novo_item)
        db.session.commit()
        
        return jsonify(novo_item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@wishlist_bp.route('/wishlist', methods=['GET'])
@swag_from({
    'tags': ['Lista de Desejos'],
    'summary': 'Lista todos os itens da lista de desejos',
    'parameters': [
        {
            'name': 'id_membro',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filtrar por membro'
        },
        {
            'name': 'prioridade',
            'in': 'query',
            'type': 'string',
            'enum': ['baixa', 'média', 'alta'],
            'required': False,
            'description': 'Filtrar por prioridade'
        }
    ],
    'responses': {
        200: {'description': 'Lista de desejos retornada com sucesso'}
    }
})
def listar_wishlist():
    try:
        query = Wishlist.query
        
        # Filtro por membro
        id_membro = request.args.get('id_membro')
        if id_membro:
            query = query.filter_by(id_membro=int(id_membro))
        
        # Filtro por prioridade
        prioridade = request.args.get('prioridade')
        if prioridade:
            query = query.filter_by(prioridade=prioridade)
        
        # Ordena por prioridade (alta primeiro) e data de adição
        items = query.order_by(
            db.case(
                (Wishlist.prioridade == 'alta', 1),
                (Wishlist.prioridade == 'média', 2),
                (Wishlist.prioridade == 'baixa', 3)
            ),
            Wishlist.data_adicao.desc()
        ).all()
        
        return jsonify([i.to_dict() for i in items]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@wishlist_bp.route('/wishlist/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['Lista de Desejos'],
    'summary': 'Busca um item específico da lista de desejos',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do item na wishlist'
        }
    ],
    'responses': {
        200: {'description': 'Item encontrado'},
        404: {'description': 'Item não encontrado'}
    }
})
def buscar_wishlist_item(id):
    try:
        item = Wishlist.query.get(id)
        if item:
            return jsonify(item.to_dict()), 200
        return jsonify({'erro': 'Item não encontrado na lista de desejos'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@wishlist_bp.route('/wishlist/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['Lista de Desejos'],
    'summary': 'Atualiza um item da lista de desejos',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do item na wishlist'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'prioridade': {'type': 'string', 'enum': ['baixa', 'média', 'alta']},
                    'notas': {'type': 'string'},
                    'titulo_desejado': {'type': 'string'},
                    'autor_desejado': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Item atualizado com sucesso'},
        404: {'description': 'Item não encontrado'}
    }
})
def atualizar_wishlist(id):
    try:
        item = Wishlist.query.get(id)
        if not item:
            return jsonify({'erro': 'Item não encontrado na lista de desejos'}), 404
        
        data = request.get_json()
        
        # Atualiza campos permitidos
        campos_atualizaveis = ['prioridade', 'notas', 'titulo_desejado', 'autor_desejado']
        for campo in campos_atualizaveis:
            if campo in data:
                setattr(item, campo, data[campo])
        
        db.session.commit()
        return jsonify(item.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@wishlist_bp.route('/wishlist/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['Lista de Desejos'],
    'summary': 'Remove um item da lista de desejos',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do item na wishlist'
        }
    ],
    'responses': {
        200: {'description': 'Item removido com sucesso'},
        404: {'description': 'Item não encontrado'}
    }
})
def deletar_wishlist(id):
    try:
        item = Wishlist.query.get(id)
        if not item:
            return jsonify({'erro': 'Item não encontrado na lista de desejos'}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'mensagem': 'Item removido da lista de desejos'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@wishlist_bp.route('/wishlist/<int:id>/comprar', methods=['POST'])
@swag_from({
    'tags': ['Lista de Desejos'],
    'summary': 'Marca item como comprado e cria o livro no catálogo',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do item na wishlist'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': False,
            'schema': {
                'type': 'object',
                'properties': {
                    'isbn': {'type': 'string'},
                    'editora': {'type': 'string'},
                    'ano_publicacao': {'type': 'integer'},
                    'genero': {'type': 'string'},
                    'num_paginas': {'type': 'integer'},
                    'localizacao': {'type': 'string'},
                    'valor_estimado': {'type': 'number'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Item comprado e adicionado ao catálogo'},
        404: {'description': 'Item não encontrado'}
    }
})
def marcar_como_comprado(id):
    try:
        item = Wishlist.query.get(id)
        if not item:
            return jsonify({'erro': 'Item não encontrado na lista de desejos'}), 404
        
        # Se for um livro não cadastrado, cria no catálogo
        if not item.id_livro and item.titulo_desejado:
            data = request.get_json() or {}
            
            novo_livro = Livro(
                titulo=item.titulo_desejado,
                autor=item.autor_desejado or 'Autor desconhecido',
                isbn=data.get('isbn'),
                editora=data.get('editora'),
                ano_publicacao=data.get('ano_publicacao'),
                genero=data.get('genero'),
                num_paginas=data.get('num_paginas'),
                localizacao=data.get('localizacao'),
                origem='Comprado da lista de desejos',
                valor_estimado=data.get('valor_estimado'),
                disponivel=True
            )
            
            db.session.add(novo_livro)
            db.session.flush()  # Para obter o ID do novo livro
            
            # Adiciona pontos ao membro que sugeriu
            if item.membro:
                item.membro.pontos_leitura += 30  # 30 pontos por sugestão aceita
            
            # Remove da wishlist
            db.session.delete(item)
            db.session.commit()
            
            return jsonify({
                'mensagem': 'Livro adicionado ao catálogo e removido da lista de desejos',
                'livro': novo_livro.to_dict()
            }), 200
        
        # Se já era um livro cadastrado, apenas remove da wishlist
        elif item.id_livro:
            livro = Livro.query.get(item.id_livro)
            
            # Remove da wishlist
            db.session.delete(item)
            db.session.commit()
            
            return jsonify({
                'mensagem': 'Item removido da lista de desejos',
                'livro': livro.to_dict() if livro else None
            }), 200
        
        return jsonify({'erro': 'Item inválido'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@wishlist_bp.route('/wishlist/sugestoes', methods=['GET'])
@swag_from({
    'tags': ['Lista de Desejos'],
    'summary': 'Lista livros sugeridos por múltiplos membros',
    'responses': {
        200: {'description': 'Lista de livros mais desejados'}
    }
})
def livros_mais_desejados():
    try:
        # Agrupa por título e conta quantos membros querem cada livro
        sugestoes = db.session.query(
            Wishlist.titulo_desejado,
            Wishlist.autor_desejado,
            db.func.count(Wishlist.id_membro).label('total_interessados'),
            db.func.group_concat(Membro.nome).label('membros_interessados')
        ).join(
            Membro
        ).filter(
            Wishlist.titulo_desejado.isnot(None)
        ).group_by(
            Wishlist.titulo_desejado,
            Wishlist.autor_desejado
        ).having(
            db.func.count(Wishlist.id_membro) > 1  # Pelo menos 2 pessoas querem
        ).order_by(
            db.func.count(Wishlist.id_membro).desc()
        ).all()
        
        resultado = [
            {
                'titulo': s[0],
                'autor': s[1],
                'total_interessados': s[2],
                'membros': s[3].split(',') if s[3] else []
            }
            for s in sugestoes
        ]
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500