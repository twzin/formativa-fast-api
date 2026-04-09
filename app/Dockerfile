FROM python:3.11-slim

WORKDIR /app

# Copia dependências primeiro (melhora cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do projeto
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]