FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "server:app", "--bind", "0.0.0.0:8080"]
