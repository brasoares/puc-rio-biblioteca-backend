# =====================================
# routes/avaliacoes.py - COMPLETE FILE
# =====================================
from flask import Blueprint, jsonify, request
from app import db
from models.avaliacao import Avaliacao
from models.livro import Livro
from models.membro import Membro
from flasgger import swag_from

avaliacoes_bp = Blueprint('avaliacoes', __name__)

@avaliacoes_bp.route('/avaliacoes', methods=['POST'])
@swag_from({
    'tags': ['Avaliações'],
    'summary': 'Cria uma nova avaliação de livro',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['id_membro', 'id_livro', 'nota'],
                'properties': {
                    'id_membro': {'type': 'integer'},
                    'id_livro': {'type': 'integer'},
                    'nota': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                    'comentario': {'type': 'string'},
                    'recomenda_para_idade': {'type': 'string'},
                    'tags': {'type': 'string'},
                    'leitura_completa': {'type': 'boolean'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Avaliação criada com sucesso'},
        400: {'description': 'Dados inválidos'},
        409: {'description': 'Membro já avaliou este livro'}
    }
})
def criar_avaliacao():
    try:
        data = request.get_json()
        
        # Validações
        if not all([data.get('id_membro'), data.get('id_livro'), data.get('nota')]):
            return jsonify({'erro': 'ID do membro, ID do livro e nota são obrigatórios'}), 400
        
        if data['nota'] < 1 or data['nota'] > 5:
            return jsonify({'erro': 'Nota deve estar entre 1 e 5'}), 400
        
        # Verifica se já existe avaliação
        avaliacao_existente = Avaliacao.query.filter_by(
            id_membro=data['id_membro'],
            id_livro=data['id_livro']
        ).first()
        
        if avaliacao_existente:
            return jsonify({'erro': 'Membro já avaliou este livro'}), 409
        
        # Verifica se o livro é clássico da família e nota mínima
        livro = Livro.query.get(data['id_livro'])
        if livro and livro.classicos_familia and data['nota'] < 4:
            return jsonify({'aviso': 'Clássico da família! Tem certeza que quer dar menos de 4 estrelas?'}), 200
        
        nova_avaliacao = Avaliacao(
            id_membro=data['id_membro'],
            id_livro=data['id_livro'],
            nota=data['nota'],
            comentario=data.get('comentario'),
            recomenda_para_idade=data.get('recomenda_para_idade'),
            tags=data.get('tags'),
            leitura_completa=data.get('leitura_completa', True)
        )
        
        # Adiciona pontos ao membro pela avaliação
        membro = Membro.query.get(data['id_membro'])
        if membro:
            membro.pontos_leitura += 15  # 15 pontos por avaliação
        
        db.session.add(nova_avaliacao)
        db.session.commit()
        
        return jsonify(nova_avaliacao.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@avaliacoes_bp.route('/avaliacoes/livro/<int:id_livro>', methods=['GET'])
@swag_from({
    'tags': ['Avaliações'],
    'summary': 'Lista todas as avaliações de um livro',
    'parameters': [
        {
            'name': 'id_livro',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do livro'
        }
    ],
    'responses': {
        200: {'description': 'Lista de avaliações retornada com sucesso'}
    }
})
def listar_avaliacoes_livro(id_livro):
    try:
        avaliacoes = Avaliacao.query.filter_by(id_livro=id_livro).order_by(
            Avaliacao.data_avaliacao.desc()
        ).all()
        return jsonify([a.to_dict() for a in avaliacoes]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@avaliacoes_bp.route('/avaliacoes/membro/<int:id_membro>', methods=['GET'])
@swag_from({
    'tags': ['Avaliações'],
    'summary': 'Lista todas as avaliações de um membro',
    'parameters': [
        {
            'name': 'id_membro',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do membro'
        }
    ],
    'responses': {
        200: {'description': 'Lista de avaliações retornada com sucesso'}
    }
})
def listar_avaliacoes_membro(id_membro):
    try:
        avaliacoes = Avaliacao.query.filter_by(id_membro=id_membro).order_by(
            Avaliacao.data_avaliacao.desc()
        ).all()
        return jsonify([a.to_dict() for a in avaliacoes]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@avaliacoes_bp.route('/avaliacoes/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['Avaliações'],
    'summary': 'Busca uma avaliação específica',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID da avaliação'
        }
    ],
    'responses': {
        200: {'description': 'Avaliação encontrada'},
        404: {'description': 'Avaliação não encontrada'}
    }
})
def buscar_avaliacao(id):
    try:
        avaliacao = Avaliacao.query.get(id)
        if avaliacao:
            return jsonify(avaliacao.to_dict()), 200
        return jsonify({'erro': 'Avaliação não encontrada'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@avaliacoes_bp.route('/avaliacoes/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['Avaliações'],
    'summary': 'Atualiza uma avaliação existente',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID da avaliação'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nota': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                    'comentario': {'type': 'string'},
                    'recomenda_para_idade': {'type': 'string'},
                    'tags': {'type': 'string'},
                    'leitura_completa': {'type': 'boolean'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Avaliação atualizada com sucesso'},
        404: {'description': 'Avaliação não encontrada'}
    }
})
def atualizar_avaliacao(id):
    try:
        avaliacao = Avaliacao.query.get(id)
        if not avaliacao:
            return jsonify({'erro': 'Avaliação não encontrada'}), 404
        
        data = request.get_json()
        
        # Validação da nota se fornecida
        if 'nota' in data:
            if data['nota'] < 1 or data['nota'] > 5:
                return jsonify({'erro': 'Nota deve estar entre 1 e 5'}), 400
            
            # Verifica se o livro é clássico da família
            livro = Livro.query.get(avaliacao.id_livro)
            if livro and livro.classicos_familia and data['nota'] < 4:
                return jsonify({'aviso': 'Clássico da família! Tem certeza que quer dar menos de 4 estrelas?'}), 200
        
        # Atualiza campos permitidos
        campos_atualizaveis = ['nota', 'comentario', 'recomenda_para_idade', 'tags', 'leitura_completa']
        for campo in campos_atualizaveis:
            if campo in data:
                setattr(avaliacao, campo, data[campo])
        
        db.session.commit()
        return jsonify(avaliacao.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@avaliacoes_bp.route('/avaliacoes/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['Avaliações'],
    'summary': 'Remove uma avaliação',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID da avaliação'
        }
    ],
    'responses': {
        200: {'description': 'Avaliação removida com sucesso'},
        404: {'description': 'Avaliação não encontrada'}
    }
})
def deletar_avaliacao(id):
    try:
        avaliacao = Avaliacao.query.get(id)
        if not avaliacao:
            return jsonify({'erro': 'Avaliação não encontrada'}), 404
        
        # Remove os pontos do membro (15 pontos que foram dados)
        membro = Membro.query.get(avaliacao.id_membro)
        if membro:
            membro.pontos_leitura = max(0, membro.pontos_leitura - 15)
        
        db.session.delete(avaliacao)
        db.session.commit()
        
        return jsonify({'mensagem': 'Avaliação removida com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@avaliacoes_bp.route('/avaliacoes/top', methods=['GET'])
@swag_from({
    'tags': ['Avaliações'],
    'summary': 'Lista os livros mais bem avaliados',
    'parameters': [
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 10,
            'description': 'Número de livros a retornar'
        }
    ],
    'responses': {
        200: {'description': 'Lista de livros mais bem avaliados'}
    }
})
def livros_mais_bem_avaliados():
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Query para pegar livros com suas médias
        livros_com_notas = db.session.query(
            Livro.id_livro,
            Livro.titulo,
            Livro.autor,
            db.func.avg(Avaliacao.nota).label('nota_media'),
            db.func.count(Avaliacao.id_avaliacao).label('total_avaliacoes')
        ).join(
            Avaliacao
        ).group_by(
            Livro.id_livro
        ).having(
            db.func.count(Avaliacao.id_avaliacao) >= 1  # Pelo menos 1 avaliação
        ).order_by(
            db.func.avg(Avaliacao.nota).desc()
        ).limit(limit).all()
        
        resultado = [
            {
                'id_livro': l[0],
                'titulo': l[1],
                'autor': l[2],
                'nota_media': round(l[3], 1),
                'total_avaliacoes': l[4]
            }
            for l in livros_com_notas
        ]
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500