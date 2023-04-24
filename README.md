# collectivo

A modular framework to build participative community platforms.

## Overview

The collectivo framework consists of a backend (this repository)
and a frontend ([collectivo-ux](https://github.com/MILA-Wien/collectivo-ux/)) application.
Different community tools can be added to collectivo through extensions.

Folders:

- `collectivo` - A django package, the core of the framework.
- `collectivo_app` - A django app that can be used to run collectivo.

## Installation

There are two ways to install collectivo:

- Using the collectivo docker image
  - For an example, see https://github.com/MILA-Wien/collectivo-mila
- Using the collectivo python package
  - Add `collectivo` to the requirements of an existing Django project
  - Adopt the settings from `collectivo_app/collectivo_app/settings.py`

### Extensions

To install a built-in extension:

- If you are using the docker image, add it to the environment variable `COLLECTIVO_EXTENSIONS`.
- If you are using the python package, add it to `INSTALLED_APPS`.

The following extensions are currently being developed:

- `members`: a membership database.
- `payments`: manage payments.
- `emails`: send automated emails.
- `shifts`: a shift management system.

### Customization

The docker image of collectivo can be combined with custom settings and extensions.
Here is an example of a file structure with various customizations:

```
- docker_compose.yml
- collectivo_custom/
    - requirements.txt
    - settings.py
    - urls.py
    - my_extension/
        - apps.py
        - ...
```

To place such a folder within the collectivo app, add a volume to `docker-compose.yml`:

```yml
collectivo:
  volumes:
    - ./collectivo_custom:/collectivo_app/collectivo_custom
```

The file `requirements.txt` can be used to add additional python packages to the container.
To install them, add the following command to `docker-compose.yml`:

```yml
command: >
  sh -c "pip install -r collectivo_custom/requirements.txt &&
         ..."
```

The file `settings.py` can be used to replace the default settings in `django_app/settings.py`
by defining the environmental variable `COLLECTIVO_SETTINGS` in `docker-compose.yml`:

```yml
environment:
  COLLECTIVO_SETTINGS: collectivo_custom.settings
```

The default settings can be imported in the new `settings.py` file to only change specific variables:

```python
from collectivo_app.settings import *
```

The file `urls.py` can be used to override the default url patterns in `django_app/urls.py` by ading the following to the new `settings.py`:

```python
ROOT_URLCONF = 'collectivo_custom.urls'
```

Finally, the folder `my_extension\` represents a custom extension, that can be installed in the new `settings.py` file as follows:

```python
INSTALLED_APPS.append('collectivo_custom.my_extension')
```

## Development

To set up a development system of collectivo on your local machine:

- Install docker and docker-compose (Version >= 20.10)
- Clone the repository with `git clone https://github.com/MILA-Wien/collectivo.git`
- Copy `.env.example` and rename it to `.env`
- Add the following line to your `/etc/hosts/` file: `127.0.0.1 keycloak collectivo.local`
- Start a local instance of collectivo with `docker compose up -d`
- Perform tests and linting with `docker compose run --rm collectivo sh -c "python manage.py test && flake8"`

The development system will be accessible via the following paths:

- Frontend: `http://collectivo.local:8001`
- Backend (API docs): `http://collectivo.local:8000/api/dev/docs/`
- Keycloak (Console): `http://keycloak:8080/admin/master/console/`

The following test users can be used to log in on the development system:

- `test_superuser@example.com`
- `test_member_01@example.com`, `test_member_02@example.com`, `test_member_03@example.com`
- `test_user_not_verified@example.com`
- `test_user_not_member@example.com`

The password for all users is `Test123!`.

To set up a development server for the frontend, follow the instructions at [collectivo-ux](https://github.com/MILA-Wien/collectivo-ux/)

## API Documentation

The API is documented automatically with SWAGGER UI and can be viewed via `/api/dev/docs/`.
The API uses [AcceptHeaderVersioning](https://www.django-rest-framework.org/api-guide/versioning/#acceptheaderversioning). The version of the API is the same as the version of collectivo.

### Schemas (Work in progress)

Each endpoint has an endpoint /schema with information about the fields.

Each entry of the schema has the following possible attributes:

```python
'field_type', 'input_type',
'label', 'help_text',
'required', 'default',
'max_length', 'min_length',
'max_value', 'min_value',
'read_only', 'write_only',
'choices', 'condition'
```

The condition is structured as follows: `{'field': x, 'condition':'exact', 'value':z}` which means that field `x` should have the exact value of `z`.

The `input_type` is currently generated automatically from the `field_type` and states default html input types.

# Core extensions

## Core (collectivo.core)

This extension initializes core functionalities of collectivo, including default database entries like the main menu.

## Auth (collectivo.auth)

Namespace for extensions that deal with authentication.

### Keycloak (collectivo.auth.keycloak)

Enable authentication with [keycloak](https://www.keycloak.org/). When using this extension, keycloak access tokens can be used to authenticate requests and user data is synchronized between collectivo and keycloak.

The extension requires the following packages:

- `python-keycloak`

To install the extension, add `collectivo.auth.keycloak` to your installed apps add keycloak as a default authentication class (see [Authentication - Django REST framework](https://www.django-rest-framework.org/api-guide/authentication/)):

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "collectivo.auth.keycloak.authentication.KeycloakAuthentication",
        ...
    ],
    ...
}
```

The following variables can be set in `settings.COLLECTIVO` to configure the extension:

- `keycloak.server_url`: Path towards the keycloak server
- `keycloak.realm_name`: Name of the realm that is used for collectivo
- `keycloak.client_id`: Name of the client that is used for collectivo
- `keycloak.client_secret_key`: Secret key of the collectivo client

Further information:

- This extension uses [python-keycloak](https://github.com/marcospereirampj/python-keycloak) to access the keycloak API.
- When using the import function to set up your keycloak server, make sure to generate a new secret key for your client before using it in production.
- To export the keycloak realm including users run `docker compose exec -u 0 keycloak /opt/keycloak/bin/kc.sh export --dir /tmp/export --realm collectivo --users realm_file` Note: exporting the realm via the gui doesn't include the users. The exported files is then in the `./docker/keycloak/export` folder.
