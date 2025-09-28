from flask import Blueprint, jsonify
from models.usuario import Usuario
from models.livro import Livro

statistics_blueprint = Blueprint('stats', __name__)

# @stats_bp.route('/stats', methods=['GET'])
# def get_stats():
    # total_usuarios = Usuario.query.count()
    # total_livros = Livro.query.count()

    # return jsonify({
        # "total_usuarios": total_usuarios,
        # "total_livros": total_livros
    # })

def retrieve_statistics():
    user_count = Usuario.query.count()
    book_bount = Livro.query.count()

    statistics_data = {
        "total_usuarios": user_count,
        "total_livros": book_bount
    }

    return jsonify(statistics_data)