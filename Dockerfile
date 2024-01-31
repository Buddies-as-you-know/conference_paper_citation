ARG PYTHON_VERSION="3.10"

FROM python:${PYTHON_VERSION}-slim

ARG POETRY_HOME="/opt/poetry"
ARG POETRY_VERSION="1.6.1"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install --no-install-recommends -y make curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org/ | python3 - --version ${POETRY_VERSION} && \
    ln -s ${POETRY_HOME}/bin/poetry /usr/local/bin/poetry && \
    poetry config virtualenvs.create false

WORKDIR /app

COPY Makefile pyproject.toml poetry.lock ./
COPY backend/ ./backend/

RUN poetry install --no-root --no-ansi

CMD ["poetry", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

