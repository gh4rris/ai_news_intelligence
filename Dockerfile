FROM apache/airflow:3.2.0

COPY pyproject.toml uv.lock ./

RUN uv export --no-dev --frozen --format requirements.txt | uv pip install -r /dev/stdin