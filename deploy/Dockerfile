FROM python:3.10.7-slim-buster

RUN pip install poetry==1.1.13

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
COPY ./tnsquery /app/src/
COPY . /app/srcinstal
WORKDIR /app/src

# Copying actuall application
RUN poetry install

CMD ["/usr/local/bin/python", "-m", "tnsquery"]
