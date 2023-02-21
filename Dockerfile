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
COPY ./collectivo_app /collectivo_app

# Copy source code of the collectivo app into the test app
COPY ./collectivo /collectivo_app/collectivo

# Move working directory into the test app
WORKDIR /collectivo_app

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

# Set python path to virtual environment
ENV PATH="/py/bin:$PATH"

# Create a static folder for the app
RUN mkdir -p /collectivo_app/static | true && \
    chown -R django-user:django-user /collectivo_app && \
    chmod -R 755 /collectivo_app/static

# Allow django-user to access the virtual environment
RUN chown -R django-user:django-user /py

# Switch to the new user
USER django-user

# Set default command
CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "collectivo_app.wsgi:application"]
