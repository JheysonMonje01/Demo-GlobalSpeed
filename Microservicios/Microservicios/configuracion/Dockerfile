FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Esto no causa errores en Windows, simplemente se ignora si no aplica
RUN chmod 600 /app/.ssh/id_rsa || true

CMD ["flask", "run", "--host=0.0.0.0", "--port=5002"]
