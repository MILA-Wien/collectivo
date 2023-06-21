# Getting started

This tutorial will show you how to quickly set up your own local instance of Collectivo.

Install the following requirements:

- [Docker](https://docs.docker.com/get-docker/) (Version >= 20.10)

Add the following line to your [hosts file](https://www.howtogeek.com/27350/beginner-geek-how-to-edit-your-hosts-file/):

```title="etc/hosts"
127.0.0.1 keycloak
```

In your project folder, clone the collectivo quickstart repository and start a local instance:

```sh
git clone https://github.com/MILA-Wien/collectivo-quickstart .
cp .env.example .env
docker compose up -d
```

You can now go to [`127.0.0.1:8001`](http://127.0.0.1:8001) and log in to Collectivo as `test_superuser@example.com` with the pasword `Test123!`.
