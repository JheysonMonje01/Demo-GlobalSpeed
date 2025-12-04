from app import bcrypt

def hash_password(plain_password):
    return bcrypt.generate_password_hash(plain_password).decode('utf-8')

def verificar_password(plain_password, hashed_password):
    return bcrypt.check_password_hash(hashed_password, plain_password)
