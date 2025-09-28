from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flasgger import Swagger
from datetime import datetime
import os

# Initialize extensions without app
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca_familiar.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-biblioteca-familiar-2024')
    
    # Swagger configuration
    app.config['SWAGGER'] = {
        'title': 'Biblioteca Familiar API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'Sistema de gerenciamento de biblioteca familiar - controle empréstimos, wishlist e avaliações',
        'termsOfService': '/terms',
        'contact': {
            'email': 'admin@bibliotecafamiliar.com'
        }
    }
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*'])
    Swagger(app)
    
    with app.app_context():
        # Import models here to avoid circular imports
        from models import membro, livro, emprestimo, avaliacao, wishlist
        
        # Create tables if they don't exist
        db.create_all()
        
        # Import and register blueprints
        from routes.membros import membros_bp
        from routes.livros import livros_bp
        from routes.emprestimos import emprestimos_bp
        from routes.estatisticas import estatisticas_bp
        from routes.avaliacoes import avaliacoes_bp
        from routes.wishlist import wishlist_bp
        
        app.register_blueprint(membros_bp, url_prefix='/api')
        app.register_blueprint(livros_bp, url_prefix='/api')
        app.register_blueprint(emprestimos_bp, url_prefix='/api')
        app.register_blueprint(estatisticas_bp, url_prefix='/api')
        app.register_blueprint(avaliacoes_bp, url_prefix='/api')
        app.register_blueprint(wishlist_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)