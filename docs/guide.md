# User guide

Step-by-step instructions on how to use Collectivo.

## Installation

To install Collectivo, follow these steps:

- Install [Docker](https://docs.docker.com/get-docker/) (Version >= 20.10)

- Clone the collectivo quickstart repository and set up a fresh environment file.

    ```sh
    git clone https://github.com/MILA-Wien/collectivo-quickstart .
    cp .env.example .env
    ```

## Local instance

To run a local instance of Collectivo, follow these steps:

- Add the following line to your [hosts file](https://www.howtogeek.com/27350/beginner-geek-how-to-edit-your-hosts-file/):

    ```title="etc/hosts"
    127.0.0.1 keycloak
    ```

- Run `docker compose up -d` to start the server.

- You can now go to [`127.0.0.1:8001`](http://127.0.0.1:8001) and log in to Collectivo as `test_superuser@example.com` with the pasword `Test123!`.


## Configuration

To configure collectivo, follow these steps:

- Change the custom settings in [`collectivo.yml`](reference.md#backend-settings).

## Deployment

To deploy collectivo, follow these steps:

- Follow the [installation](guide.md#installation) instructions.
- Change `docker-compose.production.yml` to `docker-compose.yml`.
- Adapt the variables of `.env` to your server and define new secret keys.
- Run `docker-compose up -d` to start the server.
