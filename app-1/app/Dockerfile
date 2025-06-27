# Usa uma imagem base Python oficial mais leve
FROM python:3.11-slim

# Instala dependências do sistema necessárias para psutil
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Cria usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash darede
RUN chown -R darede:darede /app

# Copia os arquivos requirements.txt para o contêiner
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos para o contêiner
COPY . .

# Muda para o usuário não-root
USER darede

# Expõe a porta 5000
EXPOSE 5000

# Adiciona labels para melhor organização
LABEL maintainer="Darede Tech Team"
LABEL description="Prometheus Tech Talk Demo Application"
LABEL version="1.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)"

# Comando para iniciar a aplicação
CMD ["python", "app.py"]
