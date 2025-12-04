# Dockerfile para pagos_service

FROM python:3.10-slim

# Seteo del directorio de trabajo
WORKDIR /app

# Copia de archivos
COPY . /app

# Instalación de dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Puerto expuesto
EXPOSE 5008

# Comando para ejecutar el servidor
CMD ["python", "main.py"]
