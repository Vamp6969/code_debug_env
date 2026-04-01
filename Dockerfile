FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir openenv-core fastapi uvicorn

COPY models.py .
COPY client.py .
COPY inference.py .
COPY __init__.py .
COPY server/ server/

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
