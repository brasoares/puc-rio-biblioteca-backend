from flask import Blueprint, jsonify
from models.membro import Membro
from models.livro import Livro
from models.emprestimo import Emprestimo
from models.avaliacao import Avaliacao
from app import db
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from flasgger import swag_from

estatisticas_bp = Blueprint('estatisticas', __name__)

@estatisticas_bp.route('/estatisticas', methods=['GET'])
@swag_from({
    'tags': ['Estatísticas'],
    'summary': 'Retorna estatísticas completas do sistema',
    'responses': {
        200: {
            'description': 'Estatísticas retornadas com sucesso',
            'schema': {
                'type': 'object',
                'properties': {
                    'resumo_geral': {'type': 'object'},
                    'leituras': {'type': 'object'},
                    'rankings': {'type': 'object'},
                    'tendencias': {'type': 'object'}
                }
            }
        }
    }
})
def obter_estatisticas():
    try:
        # Estatísticas gerais
        total_membros = Membro.query.filter_by(ativo=True).count()
        total_livros = Livro.query.count()
        livros_disponiveis = Livro.query.filter_by(disponivel=True).count()
        total_emprestimos = Emprestimo.query.count()
        emprestimos_ativos = Emprestimo.query.filter_by(status='ativo').count()
        
        # Valor total da biblioteca
        valor_total = db.session.query(func.sum(Livro.valor_estimado)).scalar() or 0
        
        # Estatísticas de leitura (últimos 30 dias)
        um_mes_atras = datetime.utcnow() - timedelta(days=30)
        livros_lidos_mes = Emprestimo.query.filter(
            and_(
                Emprestimo.status == 'devolvido',
                Emprestimo.data_devolucao >= um_mes_atras
            )
        ).count()
        
        # Gênero mais popular
        genero_popular = db.session.query(
            Livro.genero,
            func.count(Emprestimo.id_emprestimo).label('total')
        ).join(Emprestimo).group_by(Livro.genero).order_by(
            func.count(Emprestimo.id_emprestimo).desc()
        ).first()
        
        # Leitor do mês (mais empréstimos devolvidos)
        leitor_mes = db.session.query(
            Membro.nome,
            func.count(Emprestimo.id_emprestimo).label('total')
        ).join(Emprestimo).filter(
            and_(
                Emprestimo.status == 'devolvido',
                Emprestimo.data_devolucao >= um_mes_atras,
                Emprestimo.tipo_emprestimo == 'interno'
            )
        ).group_by(Membro.id_membro).order_by(
            func.count(Emprestimo.id_emprestimo).desc()
        ).first()
        
        # Livros mais emprestados
        livros_populares = db.session.query(
            Livro.titulo,
            Livro.autor,
            func.count(Emprestimo.id_emprestimo).label('total')
        ).join(Emprestimo).group_by(Livro.id_livro).order_by(
            func.count(Emprestimo.id_emprestimo).desc()
        ).limit(5).all()
        
        # Ranking de leitores por pontos
        ranking_leitores = Membro.query.filter_by(ativo=True).order_by(
            Membro.pontos_leitura.desc()
        ).limit(5).all()
        
        # Taxa de atraso
        emprestimos_atrasados = Emprestimo.query.filter_by(status='atrasado').count()
        taxa_atraso = (emprestimos_atrasados / total_emprestimos * 100) if total_emprestimos > 0 else 0
        
        # Clássicos da família
        total_classicos = Livro.query.filter_by(classicos_familia=True).count()
        
        return jsonify({
            'resumo_geral': {
                'total_membros': total_membros,
                'total_livros': total_livros,
                'livros_disponiveis': livros_disponiveis,
                'livros_emprestados': total_livros - livros_disponiveis,
                'valor_total_biblioteca': round(valor_total, 2),
                'total_emprestimos_historico': total_emprestimos,
                'total_classicos_familia': total_classicos
            },
            'leituras': {
                'emprestimos_ativos': emprestimos_ativos,
                'livros_lidos_ultimo_mes': livros_lidos_mes,
                'genero_mais_popular': genero_popular[0] if genero_popular else None,
                'leitor_do_mes': leitor_mes[0] if leitor_mes else 'Nenhum',
                'taxa_atraso': round(taxa_atraso, 1)
            },
            'rankings': {
                'livros_mais_emprestados': [
                    {'titulo': l[0], 'autor': l[1], 'total': l[2]} 
                    for l in livros_populares
                ],
                'top_leitores': [
                    {'nome': m.nome, 'pontos': m.pontos_leitura, 'nivel': m.calcular_nivel()}
                    for m in ranking_leitores
                ]
            },
            'tendencias': {
                'media_emprestimos_por_mes': round(total_emprestimos / 12, 1) if total_emprestimos > 0 else 0,
                'percentual_livros_emprestados': round((total_livros - livros_disponiveis) / total_livros * 100, 1) if total_livros > 0 else 0
            }
        }), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500