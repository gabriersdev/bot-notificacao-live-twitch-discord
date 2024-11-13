# Use uma imagem base Python adequada (com a versão que seu projeto precisa)
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos de requisitos (se houver)
COPY requirements.txt .

# Instala as dependências do projeto
RUN pip install -r requirements.txt

# Copia o código-fonte do projeto
COPY . .

# Define a porta que a aplicação irá expor
EXPOSE 8000

# Comando para executar a aplicação
CMD ["python", "Main.py"]