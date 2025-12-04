#!/bin/sh

echo "[🕒 $(date)] Iniciando verificación de órdenes vencidas..."

# Realizar la solicitud al microservicio de pagos
RESPONSE=$(curl -s -X PUT http://pagos:5008/orden_pago/verificar-vencimientos)

echo "[📦 Respuesta de /ordenes-pago/verificar-vencimientos]"
echo "$RESPONSE"

echo "[✅ $(date)] Verificación finalizada."
