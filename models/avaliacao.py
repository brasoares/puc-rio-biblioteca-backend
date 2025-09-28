from app import db
from datetime import datetime

class Avaliacao(db.Model):
    __tablename__ = 'avaliacoes'

    id_avaliacao = db.Column(db.Integer, primary_key=True)
    id_membro = db.Column(db.Integer, db.ForeignKey('membros_familia.id_membro'), nullable=False)
    id_livro = db.Column(db.Integer, db.ForeignKey('livros.id_livro'), nullable=False)
    nota = db.Column(db.Integer, nullable=False) # 1-5 estrelas
    comentario = db.Column(db.Text)
    recomenda_para_idade = db.Column(db.String(20))
    tags = db.Column(db.String(200)) # Tags separadas por vírgula
    data_avaliacao = db.Column(db.DateTime, default=datetime.now)
    leitura_completa = db.Column(db.Boolean, default=True)

    # Relacionamentos
    membro = db.relationship('Membro', back_populates='avaliacoes')
    livro = db.relationship('Livro', back_populates='avaliacoes')

    def to_dict(self):
        return {
            'id_avaliacao': self.id_avaliacao,
            'id_membro': self.id_membro,
            'id_livro': self.id_livro,
            'nome_membro': self.membro.nome if self.membro else None,
            'titulo_livro': self.livro.titulo if self.livro else None,
            'nota': self.nota,
            'comentario': self.comentario,
            'recomenda_para_idade': self.recomenda_para_idade,
            'tags': self.tags.split(',') if self.tags else [],
            'data_avaliacao': self.data_avaliacao.isoformat() if self.data_avaliacao else None,
            'leitura_completa': self.leitura_completa
        }