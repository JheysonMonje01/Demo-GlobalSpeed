FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto
EXPOSE 5005

# Comando para ejecutar la app
CMD ["python", "main.py"]
