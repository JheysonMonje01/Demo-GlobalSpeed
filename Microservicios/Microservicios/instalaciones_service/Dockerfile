# Imagen base oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias (LibreOffice, etc.)
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-dejavu \
    fonts-liberation \
    fonts-freefont-ttf \
    curl \
    libgl1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que usa Flask
EXPOSE 5010

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]
