from app.db import db

class Cliente(db.Model):
    __tablename__ = 'cliente'

    id_cliente = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona', ondelete='CASCADE'), unique=True, nullable=False)
