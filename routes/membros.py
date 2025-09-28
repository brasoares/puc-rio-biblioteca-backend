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
                        'email': {'type': 'string'},
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