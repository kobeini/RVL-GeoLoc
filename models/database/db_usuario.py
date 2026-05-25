from config import db


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable = True)
    email = db.Column(db.String(255), nullable = False, unique = True) 
    senha = db.Column(db.String(255), nullable = False)
    permissao = db.Column(db.String(20), default = 'usuario')
    
    def __init__(self, nome, email, senha, permissao):
        self.nome = nome
        self.email = email
        self.senha = senha 
        self.permissao = permissao
        
        