FROM --platform=linux/amd64 python:3.10.8-buster

RUN pip install poetry==1.3.1

# Configuring poetry
COPY pyproject.toml poetry.lock /app/src/
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY ./tnsquery /app/src/
COPY . /app/src
COPY .env /app/src/.env
WORKDIR /app/src

# Copying actuall application
RUN poetry install

CMD ["/usr/local/bin/python", "-m", "tnsquery"]
