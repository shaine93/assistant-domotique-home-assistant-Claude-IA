ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip py3-requests py3-matplotlib
RUN pip3 install --no-cache-dir --break-system-packages anthropic

COPY run.sh /
COPY ../assistant.py /app/
COPY ../deploy_server.py /app/
COPY ../config.py /app/
COPY ../i18n.py /app/

RUN chmod a+x /run.sh

WORKDIR /app
CMD ["/run.sh"]
