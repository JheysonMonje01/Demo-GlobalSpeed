import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "otra-clave")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tu_clave_secreta_para_jwt")

    # SendGrid settings (añade estas líneas)
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_SENDER_EMAIL")
