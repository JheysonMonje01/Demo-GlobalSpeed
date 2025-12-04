FROM python:3.11-slim

# Evitar problemas de timezone
ENV TZ=America/Guayaquil

# Crear y definir el directorio de trabajo
WORKDIR /app

# Copiar primero los requirements para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente
COPY . .

# Asegurar que el archivo de credenciales exista y se copie bien
COPY ./credentials/chatbotglobalspeed-omcn-da91a0d9182d.json /app/credentials/

# Variables de entorno necesarias para Flask
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/chatbotglobalspeed-omcn-da91a0d9182d.json

# Exponer el puerto por si quieres mapearlo en docker-compose
EXPOSE 5009

# Comando para correr el microservicio
CMD ["python", "main.py"]
