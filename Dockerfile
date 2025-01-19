# Usar uma imagem base Python
FROM python:3.10-slim

# Instalar dependências do sistema necessárias para o FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Instalar as dependências do projeto
WORKDIR /app
COPY . /app

# Instalar dependências do Python (se você tiver um requirements.txt)
RUN pip install -r requirements.txt

# Expor a porta do app (caso necessário)
EXPOSE 5000

# Comando para rodar o bot
CMD ["python", "bot.py"]
