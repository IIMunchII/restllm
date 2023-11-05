FROM python:3.11-buster

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock /app/
COPY ./src /app/src

RUN pip install poetry && \
    poetry install

CMD ["poetry", "run", "uvicorn", "restllm.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
