# tnsquery

`tnsquery` is an asynchronous API for performing simple transient data queries from the Transient Name Server (TNS),
or from a local postgres database. It uses async FastAPI, with SQLAlchemy to interface with the database,
uvicorn for the webserver, and HTTPX.AsyncClient to make requests to TNS and other astronomical public APIs.

The API is purposefully limited to only making object get queries to the TNS using the snphot_bot,
with no associated photometry/spectra downloaded, to minimize server load on TNS and hopefully allow
the API to be open to the public, pending approval from the TNS.

The goal is for this to integrate with services such as `astropy.coordinates.SkyCoord` to provide
an easy way to query for coordinates and other basic information for transients/supernovae, without
requiring users to create their own TNS bots and manage their API_KEY, user-agent info, and quotas.
It also integrates with https://github.com/emirkmo/supernova supernova analysis package for easily
converting photometry to publication ready lightcurves, plots, bolometric lightcurve fits, and more.
Photometry can be generated using https://github.com/SNflows/flows https://github.com/emirkmo/ztfphot
or downloaded from public surveys, etc., while the basic trabsient info can be programtically retreieved
using `tnsquery`.

...in Development. Currently The TNS API, the Postgres database local API, and the web deployment work.
Todo: 
 1 - IRSA E(B-V) automatic look-up using astroquery.
 2 - Deploy publicly behind nginx on local domain.
 3 - Add log-based limits.



The project structure was generated using fastapi_template and the webserver and database run on docker containers.

## Poetry

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m tnsquery
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/

## Docker

You can start the project with docker using this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . up --build
```

If you want to develop in docker with autoreload add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up
```

This command exposes the web application on port 8000, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . build
```

## Project structure

```bash
$ tree "tnsquery"
tnsquery
├── conftest.py  # Fixtures for all tests.
├── db  # module contains db configurations
│   ├── dao  # Data Access Objects. Contains different classes to interact with database.
│   └── models  # Package contains different models for ORMs.
├── __main__.py  # Startup script. Starts uvicorn.
├── services  # Package for different external services such as rabbit or redis etc.
├── settings.py  # Main configuration settings for project.
├── static  # Static content.
├── tests  # Tests for project.
└── web  # Package contains web server. Handlers, startup config.
    ├── api  # Package with all handlers.
    │   └── router.py  # Main router.
    ├── application.py  # FastAPI application configuration.
    └── lifetime.py  # Contains actions to perform on startup and shutdown.
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here.

All environment variabels should start with "TNSQUERY_" prefix.

For example if you see in your "tnsquery/settings.py" a variable named like
`random_parameter`, you should provide the "TNSQUERY_RANDOM_PARAMETER"
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `tnsquery.settings.Settings.Config`.

An exmaple of .env file:
```bash
TNSQUERY_RELOAD="True"
TNSQUERY_PORT="8000"
TNSQUERY_ENVIRONMENT="dev"
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code);
* mypy (validates types);
* isort (sorts imports in all files);
* flake8 (spots possibe bugs);
* yesqa (removes useless `# noqa` comments).


You can read more about pre-commit here: https://pre-commit.com/

## Migrations

If you want to migrate your database, you should run following commands:
```bash
# To run all migrations untill the migration with revision_id.
alembic upgrade "<revision_id>"

# To perform all pending migrations.
alembic upgrade "head"
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
 alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```


## Running tests

If you want to run it in docker, simply run:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . run --rm api pytest -vv .
docker-compose -f deploy/docker-compose.yml --project-directory . down
```

For running tests on your local machine.
1. you need to start a database.

I prefer doing it with docker:
```
docker run -p "5432:5432" -e "POSTGRES_PASSWORD=tnsquery" -e "POSTGRES_USER=tnsquery" -e "POSTGRES_DB=tnsquery" postgres:13.6-bullseye
```


2. Run the pytest.
```bash
pytest -vv .
```
