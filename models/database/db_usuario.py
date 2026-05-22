from config import db


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255))
    email = db.Column(db.String(255)) 
    senha = db.Column(db.String(255))
    
    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha 
        
        