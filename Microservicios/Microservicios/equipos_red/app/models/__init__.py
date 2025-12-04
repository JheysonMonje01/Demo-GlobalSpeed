from app.models.onu import ONU
from app.models.caja_nap import CajaNAP
from app.models.puerto_pon_olt import PuertoPONOLT
from app.extensions import db

# Relación después de definir los modelos
CajaNAP.onus = db.relationship("ONU", back_populates="caja", cascade="all, delete-orphan", lazy=True)
ONU.caja = db.relationship("CajaNAP", back_populates="onus", lazy=True)

PuertoPONOLT.onus = db.relationship("ONU", back_populates="puerto_pon", cascade="all, delete-orphan", lazy=True)
ONU.puerto_pon = db.relationship("PuertoPONOLT", back_populates="onus", lazy=True)
