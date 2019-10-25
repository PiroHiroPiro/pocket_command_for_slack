FROM python:3.6

WORKDIR /usr/src/source

ENV PIPENV_VENV_IN_PROJECT=1

COPY ./Pipfile ./

RUN pip install --upgrade pip \
    && pip install pipenv \
    && pipenv install --skip-lock --system --dev
