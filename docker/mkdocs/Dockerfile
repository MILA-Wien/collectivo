FROM python:3.11-slim-buster

LABEL maintainer="peaceiris"

# Install requirements
COPY ./docker/mkdocs/requirements.txt /root
WORKDIR /root
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r ./requirements.txt && \
    python3 -m pip check

# Expose MkDocs development server port
WORKDIR /home
EXPOSE 8000

# Start development server by default
CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]
