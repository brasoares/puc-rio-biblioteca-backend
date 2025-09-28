from flask import Blueprint, jsonify, request
from app import db
from models.emprestimo import Emprestimo
from models.livro import Livro
from models.membro import Membro
from datetime import datetime, timedelta
from flasgger import swag_from

emprestimos_bp = Blueprint('emprestimos', __name__)

@emprestimos_bp.route('/emprestimos', methods=['POST'])
@swag_from({
    'tags': ['Empréstimos'],
    'summary': 'Realiza um novo empréstimo (família ou amigo)',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['id_livro'],
                'properties': {
                    'id_membro': {'type': 'integer', 'description': 'ID do membro (se empréstimo interno)'},
                    'id_livro': {'type': 'integer'},
                    'tipo_emprestimo': {'type': 'string', 'enum': ['interno', 'externo']},
                    'nome_amigo': {'type': 'string', 'description': 'Nome do amigo (se empréstimo externo)'},
                    'contato_amigo': {'type': 'string', 'description': 'Contato do amigo'},
                    'observacoes': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Empréstimo realizado com sucesso'},
        400: {'description': 'Livro não disponível'},
        404: {'description': 'Livro não encontrado'}
    }
})
def realizar_emprestimo():
    try:
        data = request.get_json()
        
        # Validações
        livro = Livro.query.get(data['id_livro'])
        if not livro:
            return jsonify({'erro': 'Livro não encontrado'}), 404
        
        if not livro.disponivel:
            return jsonify({'erro': 'Livro não disponível'}), 400
        
        tipo = data.get('tipo_emprestimo', 'interno')
        
        # Validação para empréstimo interno
        if tipo == 'interno':
            if not data.get('id_membro'):
                return jsonify({'erro': 'ID do membro é obrigatório para empréstimo interno'}), 400
            
            membro = Membro.query.get(data['id_membro'])
            if not membro:
                return jsonify({'erro': 'Membro não encontrado'}), 404
            
            if not membro.ativo:
                return jsonify({'erro': 'Membro inativo'}), 400
        
        # Validação para empréstimo externo
        elif tipo == 'externo':
            if not data.get('nome_amigo'):
                return jsonify({'erro': 'Nome do amigo é obrigatório para empréstimo externo'}), 400
        
        # Cria o empréstimo
        novo_emprestimo = Emprestimo(
            id_membro=data.get('id_membro', 1),  # Default para admin se for externo
            id_livro=data['id_livro'],
            tipo_emprestimo=tipo,
            nome_amigo=data.get('nome_amigo'),
            contato_amigo=data.get('contato_amigo'),
            observacoes=data.get('observacoes')
        )
        
        # Atualiza disponibilidade do livro
        livro.disponivel = False
        
        db.session.add(novo_emprestimo)
        db.session.commit()
        
        return jsonify(novo_emprestimo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@emprestimos_bp.route('/emprestimos/<int:id>/devolver', methods=['PUT'])
@swag_from({
    'tags': ['Empréstimos'],
    'summary': 'Realiza a devolução de um livro',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do empréstimo'
        }
    ],
    'responses': {
        200: {'description': 'Devolução realizada com sucesso'},
        404: {'description': 'Empréstimo não encontrado'}
    }
})
def devolver_livro(id):
    try:
        emprestimo = Emprestimo.query.get(id)
        if not emprestimo:
            return jsonify({'erro': 'Empréstimo não encontrado'}), 404
        
        if emprestimo.status == 'devolvido':
            return jsonify({'erro': 'Livro já foi devolvido'}), 400
        
        emprestimo.status = 'devolvido'
        emprestimo.data_devolucao = datetime.utcnow()
        
        # Atualiza disponibilidade do livro
        livro = Livro.query.get(emprestimo.id_livro)
        livro.disponivel = True
        
        # Adiciona pontos de leitura se for membro da família
        pontos_base = 0
        if emprestimo.tipo_emprestimo == 'interno' and emprestimo.membro:
            # Calcula pontos baseado no número de páginas
            pontos_base = 10
            if livro.num_paginas:
                pontos_base = min(100, livro.num_paginas // 10)
            
            # Bônus por devolver no prazo
            if emprestimo.calcular_dias_atraso() == 0:
                pontos_base += 20
            
            emprestimo.membro.pontos_leitura += pontos_base
        
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Devolução realizada com sucesso',
            'emprestimo': emprestimo.to_dict(),
            'pontos_ganhos': pontos_base if emprestimo.tipo_emprestimo == 'interno' else 0
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@emprestimos_bp.route('/emprestimos', methods=['GET'])
@swag_from({
    'tags': ['Empréstimos'],
    'summary': 'Lista todos os empréstimos com filtros',
    'parameters': [
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'enum': ['ativo', 'devolvido', 'atrasado', 'todos']
        },
        {
            'name': 'tipo',
            'in': 'query',
            'type': 'string',
            'enum': ['interno', 'externo', 'todos']
        }
    ],
    'responses': {
        200: {'description': 'Lista de empréstimos'}
    }
})
def listar_emprestimos():
    try:
        query = Emprestimo.query
        
        status = request.args.get('status')
        if status and status != 'todos':
            query = query.filter_by(status=status)
        
        tipo = request.args.get('tipo')
        if tipo and tipo != 'todos':
            query = query.filter_by(tipo_emprestimo=tipo)
        
        emprestimos = query.order_by(Emprestimo.data_emprestimo.desc()).all()
        
        # Atualiza status de atrasados
        for emp in emprestimos:
            if emp.status == 'ativo' and emp.calcular_dias_atraso() > 0:
                emp.status = 'atrasado'
        
        db.session.commit()
        
        return jsonify([e.to_dict() for e in emprestimos]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@emprestimos_bp.route('/emprestimos/membro/<int:id_membro>', methods=['GET'])
def listar_emprestimos_membro(id_membro):
    try:
        emprestimos = Emprestimo.query.filter_by(id_membro=id_membro).order_by(
            Emprestimo.data_emprestimo.desc()
        ).all()
        return jsonify([e.to_dict() for e in emprestimos]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500