# collectivo

A modular framework to build participative community platforms.

## Overview

The collectivo framework consists of a backend (this repository)
and a frontend ([collectivo-ux](https://github.com/MILA-Wien/collectivo-ux/)) application.
Different community tools can be added to collectivo through extensions.

Folders:
- `collectivo` - A django package, the core of the framework.
- `collectivo_app` - A django app that can be used to run collectivo.

## Development

To run and test the app with docker:

* Install docker and docker-compose (Version >= 20.10)
* Clone the repository with `git clone https://github.com/MILA-Wien/collectivo.git`
* Add the following line to your `/etc/hosts/` file: `127.0.0.1 keycloak collectivo.local`
* Copy `.env.example` to `.env`
    - Optional: Fill out the email variables if you want to test the email features
* To start a local instance of collectivo, run: `docker compose up -d`
    - Optional: To set up a development server for the backend, use `docker compose -f docker-compose.dev.yml up -d`
    - Optional: To set up a development server for the frontend, follow the instructions at [collectivo-ux](https://github.com/MILA-Wien/collectivo-ux/)
* To open the API docs, go to `collectivo.local:8000/api/docs/`
* To open the frontend, go to `collectivo.local:8001`
    - Optional: If you set up a development server for the frontend, go to `collectivo.local:5137`
* To perform tests and linting, run: `docker compose run --rm collectivo sh -c "python manage.py test && flake8"`

## Installation

To install collectivo, there are two ways:

- Using docker
    - Copy `.env.example` to `.env`
- Using collectivo as a Django app within your existing Django project
    - Add `collectivo` to the requirements of your Django project
    - Add collectivo modules to your installed apps like in `collectivo_app/collectivo_app/settings.py`

## API

The API is documented automatically with SWAGGER UI and can be viewed via `/api/docs/`.
The API uses [AcceptHeaderVersioning](https://www.django-rest-framework.org/api-guide/versioning/#acceptheaderversioning). The version of the API is the same as the version of collectivo.

### Schemas

Each endpoint has now an endpoint /schema with information about the fields.

The schema has the following possible attributes:

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


## Built-in extensions

To install a built-in extension:

- If you are using the docker image, add it to the environment variable `COLLECTIVO_EXTENSIONS`.
- If you are using a custom django app, add it to `INSTALLED_APPS`.

### devtools

The devtools extension sets up the following test users:

- `test_superuser@example.com`
- `test_member_01@example.com`, `test_member_02@example.com`, `test_member_03@example.com`
- `test_user_not_verified@example.com`
- `test_user_not_member@example.com`

The password for all users is `Test123!`.

### auth

The auth extension manages user authentication and authorization.
Currently, the only supported authentication service is [keycloak](https://www.keycloak.org/).
To activate authentication via keycloak, add the following line in `settings.py`:

```python
MIDDLEWARE = [
    ...
    'collectivo.auth.middleware.KeycloakMiddleware'
]
```

The following attributes can be used to configure the auth extension in the collectivo settings within `settings.py`:

```python
KEYCLOAK = {
    'SERVER_URL': 'http://keycloak:8080',
    'REALM_NAME': 'collectivo',
    'CLIENT_ID': 'collectivo',
    'CLIENT_SECRET_KEY': '**********'
}
```

Further information:
- To export the keycloak realm including users run `docker compose exec -u 0 keycloak /opt/keycloak/bin/kc.sh export --dir /tmp/export --realm collectivo --users realm_file` Note: exporting the realm via the gui doesn't include the users. The exported files is then in the `./docker/keycloak/export` folder.

### members extension

The members extension can be used to manage member data.

- Roles:
    - `members_user`
    - `members_admin`
- API:
    - `/members/register`: Users that are not yet members can sign up as members. They then automatically receive the role `members_user`.
    - `/members/profile`: Members can manage their own data (required role: `members_user`).
    - `/members/members`: Manage the data of all users (required role: `members_admin` or `superuser`).
    - `/members/summary`: Get summary data of all users (required role: `members_admin` or `superuser`).

## Custom settings and extensions

When using the collectivo docker image,
a folder with custom settings and extensions can be added as a volume.

Here is an example of a folder with custom settings, url patterns, and an extension:

```
- collectivo_extensions/
    - requirements.txt
    - settings.py
    - urls.py
    - my_extension/
        - apps.py
        - ...
```

The following configuration in `docker-compose.yml`
places this folder within the collectivo app
and defines the custom settings to override the default settings.

```yml
  collectivo:
    environment:
        COLLECTIVO_SETTINGS: collectivo_extensions.settings
    volumes:
      - ./collectivo_extensions:/collectivo-app/collectivo_extensions
```

The following configuration of `collectivo_extensions/settings.py`
copies the default settings and adds the custom url patterns and extension.

```python
from collectivo_app.settings import *
INSTALLED_APPS.append('collectivo_extensions.my_extension')
ROOT_URLCONF = 'collectivo_extensions.urls'
```

TODO: How to handle requirements.txt?
