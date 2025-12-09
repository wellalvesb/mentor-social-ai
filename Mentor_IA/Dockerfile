# 1. Base Image: Usamos uma imagem Python leve e otimizada
FROM python:3.11-slim

# 2. Define o diretório de trabalho (onde o código será copiado)
WORKDIR /app

# 3. Copia a lista de dependências e instala
# Isso usa o cache do Docker, otimizando reconstruções
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia todo o código do projeto para o container
COPY . .

# 5. Expõe a porta que o Uvicorn irá usar (a porta 8000)
EXPOSE 8000

# 6. Define o comando de inicialização
# Este comando inicia o servidor Uvicorn quando o container for rodado
# NOTA: Não usamos --reload aqui, pois é código de produção/deploy.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]