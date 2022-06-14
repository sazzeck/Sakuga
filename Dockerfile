FROM python:3.9-buster

WORKDIR /sakuga

RUN apt-get update -y && apt-get upgrade -y \
    && apt update -y  && apt upgrade -y \
    && pip install poetry
    
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install -n --no-dev

COPY . ./

RUN chmod +x entrypoint.sh
ENTRYPOINT [ "sh", "entrypoint.sh" ]