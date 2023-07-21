# Development

## Set up a development environment

The following instructions will help you set up a local system for the development of Collectivo. This setup is not necessary for the development custom extensions (see [backend extensions](#backend-extensions) and [frontend extensions](#frontend-extensions)).

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

## Backend extensions

Extensions can be added to the backend of Collectivo as [Django applications](https://docs.djangoproject.com/en/4.2/ref/applications/). The extension code is added to the application through a [Docker volume](https://docs.docker.com/storage/volumes/). An alternative to extensions is to use [external services](extensions/components.md).

### Installation

Start from a clone of the [quickstart repository](quickstart.md) and create a copy of the extension template:

```shell
cd collectivo/extensions/
cp -r extension_template my_extension
```

Adapt the name of the extension in the app configuration:

```python title="collectivo/extensions/my_extension/apps.py"
class ExtensionConfig(AppConfig):
    name = "my_extension"
```

Add the name of the extension to [`collectivo.yml`](reference.md#settings):

```yaml title="collectivo/collectivo.yml"
extensions:
  - my_extension
```


### Background tasks

Collectivo uses [Celery](https://docs.celeryq.dev/en/stable/) to run background tasks. To define a new task, create a file `tasks.py` in your extension folder and add a function with the [`@shared_task`](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html#using-the-shared-task-decorator) decorator.
To avoid naming conflicts, the name of the task should start with the name of your extension. For example:

```python title="my_extension/tasks.py"

from celery import shared_task

@shared_task(name="my_extension_task")
def my_extension_task():
    print("my_extension_task has been called")
```

To define periodic tasks, create a file `schedules.py` in your extension folder and add a dictionary named `schedules`. The content of this dictionary should follow the syntax of celery's [`app.conf.beat_schedule`](https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-beat_schedule). More documentation about perodic tasks is in the [celery documentation](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html). For example:

```python title="my_extension/schedules.py"
schedules = {
    # Execute my_extension_task every 10 seconds
    "my_extension_task-10sec": {"task": "my_extension_task", "schedule": 10.0},
}
```

## Frontend extensions

Extensions can be added to the frontend of Collectivo as [Vue components](https://vuejs.org/guide/introduction.html). The extension code is added to the application in the build stage of the Docker container. An alternative to extensions is to use [external services](extensions/components.md).

### Installation

Start from a clone of the [quickstart repository](quickstart.md) and create a copy of the extension template:

```shell
cd collectivo-ux/extensions/
cp -r extension_template my_extension
```

Add the name of the extension to [`collectivo.json`](reference.md#settings):

```yaml title="collectivo-ux/collectivo.json"
{
  "extensions": ["my_extension"]
}
```
