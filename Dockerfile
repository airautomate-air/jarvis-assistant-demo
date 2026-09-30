FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY demo_server.py .
COPY static/ ./static/

EXPOSE 8080

CMD ["uvicorn", "demo_server:app", "--host", "0.0.0.0", "--port", "8080"]
