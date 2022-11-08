# Build test-extension
FROM node:18 AS build-env

# Create app directory
WORKDIR /app

ENV TZ=Europe/Vienna
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install app dependencies

COPY /collectivo-test-app/test_extension/components/package.json package.json
RUN yarn

COPY /collectivo-test-app/test_extension/components/ .

# If you are building your code for production
RUN yarn build

# Use Python runtime as parent image
FROM python:3.9-alpine3.13

# Send stdout and sterr messages directly to the terminal
ENV PYTHONUNBUFFERED 1


# Install temporary packages to build the postgresql database
RUN apk add --update --no-cache postgresql-client  && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev

# Copy further requirements into the container
COPY ./requirements.txt /tmp/requirements.txt

# Copy source code of the test app into the container
COPY ./collectivo-test-app /collectivo-test-app

# Copy source code of the collectivo app into the test app
COPY ./collectivo /collectivo-test-app/collectivo

# Copy source code of the test-extension into the test app
COPY --from=build-env /app/dist /collectivo-test-app/test_extension/static/test_extension

# Move working directory into the test app
WORKDIR /collectivo-test-app

# Set port through which the test app can be accessed
EXPOSE 8000

# Install requirements and remove temporary files
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp

# Remove temporary packages and create a new user
RUN apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

# TODO What does this do?
ENV PATH="/py/bin:$PATH"

# Create a static folder for the app
RUN mkdir -p /collectivo-test-app/static | true && \
    chown -R django-user:django-user /collectivo-test-app && \
    chmod -R 755 /collectivo-test-app/static

# Create a static folder for microfrontends
RUN mkdir -p /collectivo-test-app/test_extension/static/test_extension

# Switch to the new user
USER django-user

# Set default command
CMD while ! nc -z db 5432; do sleep 1; done && \
             python manage.py migrate && \
             python manage.py collectstatic --noinput && \
             python manage.py runserver 0.0.0.0:8000
