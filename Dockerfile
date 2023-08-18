FROM python:3.10-alpine AS base

LABEL version="1.0"
LABEL description="docker-dbms-backup"

ARG TZ='Europe/Rome'
ENV TZ ${TZ}

RUN apk add --no-cache \
    tzdata  \
    postgresql14-client \
    mariadb-client \
    gzip \
    bzip2

RUN ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo "${TZ}" > /etc/timezone

WORKDIR /app


FROM base as build

WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt


FROM build as final

WORKDIR /app

COPY main.py .
COPY configuration.py .
COPY aws/* aws/
COPY compressor/* compressor/
COPY dbms/* dbms/

ENTRYPOINT ["python", "./main.py"]
