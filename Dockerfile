FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY assistant.py .
COPY deploy_server.py .
COPY config.py .
COPY i18n.py .

VOLUME /app/data

CMD ["python3", "assistant.py"]
