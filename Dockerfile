FROM python:3.9-buster

WORKDIR /sakuga

RUN apt-get update -y && apt-get upgrade -y \
    && apt update -y  && apt upgrade -y \
    python -m pip install --upgrade pip \
    && pip install 
    
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . ./

RUN chmod +x entrypoint.sh
ENTRYPOINT [ "sh", "entrypoint.sh" ]