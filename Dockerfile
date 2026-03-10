FROM apache/airflow:3.1.7

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

CMD ["python", "-m", "src.main"]