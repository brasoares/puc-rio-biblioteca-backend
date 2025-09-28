from app import db
from datetime import datetime, timedelta

class Emprestimo(db.Model):
    __tablename__ = 'emprestimos'

    id_emprestimo = db.Column(db.Integer, primary_key=True)
    id_membro = db.Column(db.Integer, db.ForeignKey('membros_familia.id_membro'), nullable=False)
    id_livro = db.Column(db.Integer, db.ForeignKey('livros.id_livro'), nullable=False)
    data_emprestimo = db.Column(db.DateTime, default=datetime.now)
    data_prevista_devolucao = db.Column(db.DateTime)
    data_devolucao = db.Column(db.DateTime)
    tipo_emprestimo =db.Column(db.String(20), default='interno') # interno, externo (amigos)
    nome_amiga = db.Column(db.String(100)) # Se empréstimo para pessoa amiga
    contato_emprestimo = db.Column(db.String(100)) # Telefone/email da pessoa amiga
    status = db.Column(db.String(20), default='ativo') # ativo, devolvido, atrasado, perdido
    observacoes = db.Column(db.Text)

    # Relacionamentos
    membro = db.relationship('Membro', back_populates='emprestimos')
    livro = db.relationship('Livro', back_populates='emprestimos')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.data_prevista_devolucao:
            # 30 dias para família, 14 para amizades
            dias = 30 if self.tipo_emprestimo == 'interno' else 14
            self.data_prevista_devolucao = datetime.now() + timedelta(days=dias)

    def to_dict(self):
        return {
            'id_emprestimo': self.id_emprestimo,
            'id_membro': self.id_membro,
            'id_livro': self.id_livro,
            'nome_membro': self.membro.nome if self.membro else None,
            'titulo_livro': self.livro.titulo if self.livro else None,
            'tipo_emprestimo': self.tipo_emprestimo,
            'nome_amiga': self.nome_amiga,
            'contato_emprestimo': self.contato_emprestimo,
            'data_emprestimo': self.data_emprestimo.isoformat() if self.data_emprestimo else None,
            'data_prevista_devolucao': self.data_prevista_devolucao.isoformat() if self.data_prevista_devolucao else None,
            'data_devolucao': self.data_devolucao.isoformat() if self.data_devolucao else None,
            'status': self.status,
            'dias_atraso': self.calcular_dias_atraso(),
            'observacoes': self.observacoes
        }
    
    def calcular_dias_atraso(self):
        if self.status == 'devolvido' or not self.data_prevista_devolucao:
            return 0
        hoje = datetime.now()
        if hoje > self.data_prevista_devolucao:
            return (hoje - self.data_prevista_devolucao).days
        return 0