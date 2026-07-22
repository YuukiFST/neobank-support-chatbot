FROM python:3.12-slim AS base
WORKDIR /app
RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN uv pip install --system --no-cache .

COPY services/ingestion_worker/ services/ingestion_worker/
COPY shared/ shared/
COPY data/ data/

CMD ["python", "-m", "services.ingestion_worker.interface.worker"]
