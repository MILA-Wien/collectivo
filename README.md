# MachMit Backend

Dockerized Django REST API with a PostgreSQL database.

Based on https://github.com/LondonAppDeveloper/recipe-app-api

## Development

Requirements for the development environment that is used in our team:

1. [Docker](https://www.docker.com/), Version 20.10.
2. [VisualStudioCode](https://code.visualstudio.com/) (VSCode) with the extension "Django".

To run and test the app with docker:

- To build a development server, run: `docker compose build`
- To run a development server, run: `docker compose up -d`
- To perform tests and linting, run: `docker compose run --rm app sh -c "python manage.py test && flake8"`

## Documentation

- The API will be available at http://127.0.0.1:8000/.
- The API documentation will be available at `/api/docs/`.
- To test the frontend, you can use the API call `GET` at `/api/core/version/`.
- To test backend and frontend together, see [machmit](https://github.com/MILA-Wien/machmit).
