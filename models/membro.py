from app import db
from datetime import datetime

class Membro(db.Model):
    __tablename__ = 'membros_familia'
    
    id_membro = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    apelido = db.Column(db.String(50))
    idade = db.Column(db.Integer)
    tipo = db.Column(db.String(20), default='membro')  # membro, administrador, criança
    avatar_cor = db.Column(db.String(7), default='#3B82F6')  # Cor do avatar
    generos_favoritos = db.Column(db.String(200))  # Gêneros separados por vírgula
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    pontos_leitura = db.Column(db.Integer, default=0)  # Gamificação
    
    # Relacionamentos
    emprestimos = db.relationship('Emprestimo', back_populates='membro', lazy='dynamic')
    avaliacoes = db.relationship('Avaliacao', back_populates='membro', lazy='dynamic')
    wishlist_items = db.relationship('Wishlist', back_populates='membro', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id_membro': self.id_membro,
            'nome': self.nome,
            'email': self.email,
            'apelido': self.apelido,
            'idade': self.idade,
            'tipo': self.tipo,
            'avatar_cor': self.avatar_cor,
            'generos_favoritos': self.generos_favoritos.split(',') if self.generos_favoritos else [],
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ativo': self.ativo,
            'pontos_leitura': self.pontos_leitura,
            'nivel_leitor': self.calcular_nivel()
        }
    
    def calcular_nivel(self):
        if self.pontos_leitura < 100:
            return "Iniciante"
        elif self.pontos_leitura < 500:
            return "Leitor"
        elif self.pontos_leitura < 1000:
            return "Bookworm"
        else:
            return "Mestre dos Livros"