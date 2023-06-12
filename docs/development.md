# Development

## How to set up a development system

### Backend

Install the following requirements:

- [Docker](https://docs.docker.com/get-docker/) (Version >= 20.10)

Add the following line to your [hosts file](https://www.howtogeek.com/27350/beginner-geek-how-to-edit-your-hosts-file/):

```title="etc/hosts"
127.0.0.1 keycloak
```

In your project folder, clone the collectivo repository and start a local instance of collectivo:

```sh
git clone https://github.com/MILA-Wien/collectivo.git
cd collectivo
cp .env.example .env
docker compose up -d
```

You can now access the following pages in your browser:

- Frontend: [`http://localhost:8001`](http://localhost:8001)
- Backend: [`http://localhost:8000`](http://localhost:8000)
- Keycloak: [`http://localhost:8080`](http://localhost:8080)
- Documentation: [`http://localhost:8003`](http://localhost:8003)
- API documentation: [`http://localhost:8000/api/docs`](http://localhost:8000/api/docs)

Perform tests and linting:

```sh
docker compose run --rm collectivo sh -c "python manage.py test && flake8"
```

### Frontend (optional)

In addition to the above, you can also set up a development environment for the frontend.

Install the following requirements:

- [Yarn](https://classic.yarnpkg.com/lang/en/docs/install/)

In your project folder, clone the collectivo-ux repository and start a development server:

```sh
git clone https://github.com/MILA-Wien/collectivo-ux.git
cd collectivo-ux
yarn
yarn dev
```

You can now access the frontend at [`http://localhost:5173`](http://localhost:5173).

Perform end-to-end tests and linting:

```sh
yarn build:staging
yarn test:e2e
yarn lint
```

### Example users

If `example_data` is `true` in [collectivo.yml](reference.md#settings), the following users will be available:

- `test_superuser@example.com`
- `test_member_01@example.com`, `test_member_02@example.com`,
  `test_member_03@example.com`
- `test_user_not_verified@example.com`
- `test_user_not_member@example.com`

The password for all users is `Test123!`.