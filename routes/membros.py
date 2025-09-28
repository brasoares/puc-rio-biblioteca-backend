from flask import Blueprint, jsonify, request
from app import db
from models.membro import Membro
from flasgger import swag_from

membros_bp = Blueprint('membros', __name__)

@membros_bp.route('/membros', methods=['GET'])
@swag_from({
    'tags': ['Membros da Família'],
    'summary': 'Lista todos os membros da família',
    'responses': {
        200: {
            'description': 'Lista de membros retornada com sucesso',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id_membro': {'type': 'integer'},
                        'nome': {'type': 'string'},
                        'apelido': {'type': 'string'},
                        'idade': {'type': 'integer'},
                        'tipo': {'type': 'string'},
                        'pontos_leitura': {'type': 'integer'},
                        'nivel_leitor': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def listar_membros():
    try:
        membros = Membro.query.filter_by(ativo=True).all()
        return jsonify([m.to_dict() for m in membros]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    
@membros_bp.route('/membros/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['Membros da Família'],
    'summary': 'Busca um membro por ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do membro'
        }
    ],
    'responses': {
        200: {'description': 'Membro encontrado'},
        404: {'description': 'Membro não encontrado'}
    }
})
def buscar_membro(id):
    membro = Membro.query.get(id)
    if membro:
        return jsonify(membro.to_dict()), 200
    return jsonify({'erro': 'Membro não encontrado'}), 404