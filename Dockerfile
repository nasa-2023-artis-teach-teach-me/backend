FROM python:3.10-buster

RUN apt-get update && apt install -y curl
RUN curl -sSL https://install.python-poetry.org | python
ENV PATH="${PATH}:/root/.local/bin"
RUN poetry config virtualenvs.in-project true

WORKDIR /app
COPY poetry.toml .
COPY pyproject.toml .
RUN poetry env use /usr/local/bin/python && poetry install

COPY app app

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "--port", "8000", "app.main:app"]