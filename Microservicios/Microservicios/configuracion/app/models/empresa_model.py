from app.extensions import db

class Empresa(db.Model):
    __tablename__ = 'empresa'

    id_empresa = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    representante = db.Column(db.String(100), nullable=False)
    ruc = db.Column(db.String(13), unique=True, nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    logo = db.Column(db.LargeBinary)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    fecha_modificacion = db.Column(db.DateTime, onupdate=db.func.now())

    telefonos = db.relationship("EmpresaTelefono", backref="empresa", cascade="all, delete-orphan")
    correos = db.relationship("EmpresaCorreo", backref="empresa", cascade="all, delete-orphan")


class EmpresaTelefono(db.Model):
    __tablename__ = 'empresa_telefono'

    id_telefono = db.Column(db.Integer, primary_key=True)
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresa.id_empresa'), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    tipo = db.Column(db.String(30))  # Nueva columna
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    fecha_modificacion = db.Column(db.DateTime, onupdate=db.func.now())


class EmpresaCorreo(db.Model):
    __tablename__ = 'empresa_correo'

    id_correo = db.Column(db.Integer, primary_key=True)
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresa.id_empresa'), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(30))  # Nueva columna
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    fecha_modificacion = db.Column(db.DateTime, onupdate=db.func.now())
  
    
    
    