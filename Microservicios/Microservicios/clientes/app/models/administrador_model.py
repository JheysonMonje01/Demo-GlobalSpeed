from app.db import db

class Administrador(db.Model):
    __tablename__ = 'administrador'

    id_administrador = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona', ondelete='CASCADE'), unique=True, nullable=False)
