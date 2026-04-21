ARG BUILD_FROM
FROM $BUILD_FROM

# Dépendances système
RUN apk add --no-cache python3 py3-pip py3-requests jq curl

# Dépendances Python
RUN pip3 install --no-cache-dir --break-system-packages \
    anthropic \
    matplotlib

# Script de démarrage
COPY run.sh /
RUN chmod a+x /run.sh

# Code de l'application
COPY assistant.py        /app/
COPY deploy_server.py    /app/
COPY config.py           /app/
COPY shared.py           /app/
COPY skills.py           /app/
COPY i18n.py             /app/
COPY comportement.txt    /app/
COPY APPAREILS_CONNUS.json /app/

WORKDIR /app
CMD ["/run.sh"]
