FROM python:3.12-slim

# Dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dépendances Python (mises en cache séparément de l'app pour rebuild rapide)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code de l'application
COPY assistant.py        .
COPY deploy_server.py    .
COPY config.py           .
COPY shared.py           .
COPY skills.py           .
COPY i18n.py             .
COPY comportement.txt    .
COPY APPAREILS_CONNUS.json .

# Dossier persistant pour config.json + memory.db + logs
VOLUME ["/app/data"]
ENV CONFIG_PATH=/app/data/config.json \
    DB_PATH=/app/data/memory.db \
    LOG_PATH=/app/data/assistant.log

# Healthcheck simple : process assistant encore vivant
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f "assistant.py" >/dev/null || exit 1

CMD ["python3", "-u", "assistant.py"]
