FROM --platform=linux/amd64 python:3.10.8-buster

RUN pip install poetry==1.1.13

# Configuring poetry
COPY pyproject.toml poetry.lock /app/src/
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY ./tnsquery /app/src/
COPY . /app/src
WORKDIR /app/src

# Copying actuall application
RUN poetry install

CMD ["/usr/local/bin/python", "-m", "tnsquery"]
