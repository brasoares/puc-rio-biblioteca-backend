from app import db
from datetime import datetime

class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id_wishlist = db.Column(db.Integer, primary_key=True)
    id_membro = db.Column(db.Integer, db.ForeignKey('membros_familia.id_membro'))
    id_livro = db.Column(db.Integer, db.ForeignKey('livros.id_livro'))
    titulo_desejado = db.Column(db.String(200)) # Para livros não cadastrados
    autor_desejado = db.Column(db.String(200))
    prioridade = db.Column(db.String(20), default="média") # baixa, média, alta
    data_adicao = db.Column(db.DateTime, default=datetime.now)
    notas = db.Column(db.Text)

    # Relacionamentos
    membro = db.relationship('Membro', back_populates='wishlist_items')
    livro = db.relationship('Livro', back_populates='wishlist_items')

    def to_dict(self):
        return {
            'id_wishlist': self.id_wishlist,
            'id_membro': self.id_membro,
            'nome_membro': self.membro.none if self.membro else None,
            'id_livro': self.id_livro,
            'titulo_livro': self.livro.titulo if self.livro else self.titulo_desejado,
            'autor_livro': self.livro.autor if self.livro else self.autor_desejado,
            'prioridade': self.prioridade,
            'data_adicao': self.data_adicao.isoformat() if self.data_adicao else None,
            'notas': self.notas
        }