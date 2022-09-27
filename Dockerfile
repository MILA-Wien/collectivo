FROM python:3.9-alpine3.13
LABEL maintainer="Joël Foramitti"

ENV PYTHONUNBUFFERED 1

RUN  apk add --update --no-cache postgresql-client  && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
COPY ./.bandit /app/.bandit
COPY ./.flake8 /app/.flake8

WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp

#Clean up
RUN apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

ENV PATH="/py/bin:$PATH"

USER django-user
