FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir \
    pillow \
    requests

COPY dashboard_kindle.py /app/dashboard_kindle.py
COPY server.py /app/server.py

RUN mkdir -p /output

EXPOSE 8080

# Roda o dashboard em background com loop infinito e o servidor HTTP em foreground
CMD ["sh", "-c", "python /app/dashboard_kindle.py & python /app/server.py"]