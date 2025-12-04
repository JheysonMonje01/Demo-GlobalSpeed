FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y \
    libreoffice \
    fonts-dejavu \
    fonts-liberation \
    fonts-freefont-ttf \
    python3-pip && \
    fc-cache -f -v && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod 600 /app/.ssh/id_rsa || true

CMD ["flask", "run", "--host=0.0.0.0", "--port=5006"]
