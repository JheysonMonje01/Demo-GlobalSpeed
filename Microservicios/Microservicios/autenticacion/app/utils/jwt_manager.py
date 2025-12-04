import json
import redis
import os
from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token


# Configurar conexión con Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

def crear_token(data, expiracion=15):
    return create_access_token(
        identity=json.dumps(data),
        expires_delta=timedelta(minutes=expiracion)
    )

#CODIGO DE REDIS
def crear_refresh_token(data, expiracion=1440):
    token = create_refresh_token(
        identity=json.dumps(data),
        expires_delta=timedelta(minutes=expiracion)
    )
    redis_client.setex(f"refresh:{token}", timedelta(minutes=expiracion), "valido")
    return token

def es_refresh_token_valido(token):
    return redis_client.get(f"refresh:{token}") == "valido"

def eliminar_refresh_token(token):
    redis_client.delete(f"refresh:{token}")


