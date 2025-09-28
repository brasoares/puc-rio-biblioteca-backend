from app import db
from datetime import datetime

class Livro(db.Model):
    __tablename__ = 'livros'

    id_livro = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    editora = db.Column(db.String(100))
    ano_publicacao = db.Column(db.Integer)
    genero = db.Column(db.String(100))
    subgenero = db.Column(db.String(100))
    idioma = db.Column(db.String(30), default='Português')
    num_paginas = db.Column(db.Integer)
    idade_recomendada = db.Column(db.String(20)) # "Todas", "10+", "14+", "18+"
    localizacao = db.Column(db.String(50)) # Estante A, Prateleira 2, etc.
    estado_conservacao = db.Column(db.String(20), default='Bom') # Novo, Bom, Regular, Ruim
    disponivel = db.Column(db.Boolean, default=True)
    capa_url = db.Column(db.String(300))
    sinopse = db.Column(db.Text)
    data_aquisicao = db.Column(db.DateTime, default=datetime.now)
    origem = db.Column(db.String(100)) # Comprado, presente, Herdado, etc.
    valor_estimado = db.Column(db.Float)
    classicos_familia = db.Column(db.Boolean, default=False)

    # Relacionamentos
    emprestimos = db.relationship('Emprestimo', back_populates='livro', lazy='dynamic')
    avaliacoes = db.relationship('Avaliacao', back_populates='livro', lazy='dynamic')
    wishlist_items = db.relationship('Wishlist', back_populates='livro', lazy='dynamic')

    @property
    def status(self):
        return "disponivel" if self.disponivel else "emprestado"
    
    @property
    def nota_media(self):
        avaliacoes = self.avaliacoes.all()
        if not avaliacoes:
            return 0
        return sum(a.nota for a in avaliacoes) / len(avaliacoes)
    
    def to_dict(self):
        return {
            'id_livro': self.id_livro,
            'isbn': self.isbn,
            'titulo': self.titulo,
            'autor': self.autor,
            'editora': self.editora,
            'ano_publicacao': self.ano_publicacao,
            'genero': self.genero,
            'subgenero': self.subgenero,
            'idioma': self.idioma,
            'num_paginas': self.num_paginas,
            'idade_recomendada': self.idade_recomendada,
            'localizacao': self.localizacao,
            'estado_conservacao': self.estado_conservacao,
            'status': self.status,
            'disponivel': self.disponivel,
            'capa_url': self.capa_url,
            'sinopse': self.sinopse,
            'data_aquisicao': self.data_aquisicao.isoformat() if self.data_aquisicao else None,
            'origem': self.origem,
            'valor_estimado': self.valor_estimado,
            'classicos_familia': self.classicos_familia,
            'nota_media': round(self.nota_media, 1),
            'total_avaliacoes': self.avaliacoes.count()
        }