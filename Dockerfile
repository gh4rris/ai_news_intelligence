FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

WORKDIR /dbt_ai_news

ENV AWS_BUCKET="ai-news-bucket-666"

CMD ["dbt", "--version"]