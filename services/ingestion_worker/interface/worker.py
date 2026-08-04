"""Ingestion worker — consumes Redis jobs for KB ingestion and escalation processing."""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import TYPE_CHECKING, Any, cast

from sqlalchemy import text

from services.ingestion_worker.application.etl_pipeline import run_ingestion
from shared.infrastructure.database import async_session
from shared.infrastructure.observability import log
from shared.infrastructure.redis_client import get_redis

if TYPE_CHECKING:
    from collections.abc import Awaitable

# redis-py 5.x shares the command mixins between the sync and async clients, so every command
# is annotated `Awaitable[T] | T`. The casts below state which half applies on the async client;
# they document the library's typing, they do not assert anything about runtime values.

# Job types
JOB_INGESTION = "ingestion"
JOB_ESCALATION = "escalation"


async def process_ingestion_job(payload: dict[str, Any]) -> None:
    """Process a KB ingestion job."""
    data_dir = payload.get("data_dir", "data/kb")
    log.info("processing_ingestion_job", data_dir=data_dir)
    count = run_ingestion(data_dir)
    log.info("ingestion_job_complete", chunks=count)


async def process_escalation_job(payload: dict[str, Any]) -> None:
    """Process an escalation job — persist handoff and publish event."""
    log.info("processing_escalation_job", payload=payload)

    async with async_session() as session:
        # Persist handoff
        await session.execute(
            text(
                "INSERT INTO handoffs (id, session_id, customer_id, payload, status) "
                "VALUES (:id, :session_id, :customer_id, :payload, 'queued')"
            ),
            {
                "id": uuid.uuid4(),
                "session_id": uuid.UUID(payload["session_id"]),
                "customer_id": uuid.UUID(payload["customer_id"]),
                "payload": json.dumps(payload),
            },
        )
        await session.commit()

    # Publish escalation.created event
    redis = await get_redis()
    await redis.publish(
        "events",
        json.dumps(
            {
                "event": "escalation.created",
                "handoff_id": str(payload.get("id", "")),
                "customer_id": payload["customer_id"],
                "intent": payload.get("intent", "unknown"),
            }
        ),
    )
    await redis.close()

    log.info("escalation_job_complete", handoff_id=payload.get("id"))


async def worker_loop() -> None:
    """Main worker loop — consume jobs from Redis queue."""
    redis = await get_redis()
    log.info("ingestion_worker_started")

    while True:
        try:
            # Block-pop from queue with 5s timeout
            result = await cast(
                "Awaitable[list[Any] | None]", redis.brpop(["neobank:queue"], timeout=5)
            )
            if result is None:
                continue

            _, job_data = result
            job = json.loads(job_data)

            job_id = job.get("job_id", "unknown")
            job_kind = job.get("kind", "unknown")
            payload = job.get("payload", {})
            attempts = job.get("attempts", 0)

            log.info("job_received", job_id=job_id, kind=job_kind, attempts=attempts)

            try:
                if job_kind == JOB_INGESTION:
                    await process_ingestion_job(payload)
                elif job_kind == JOB_ESCALATION:
                    await process_escalation_job(payload)
                else:
                    log.warning("unknown_job_kind", kind=job_kind)
            except Exception as e:
                log.error("job_processing_failed", job_id=job_id, error=str(e))
                # Requeue with incremented attempts
                if attempts < 3:
                    job["attempts"] = attempts + 1
                    await cast("Awaitable[int]", redis.lpush("neobank:queue", json.dumps(job)))
                else:
                    # Dead letter
                    await cast(
                        "Awaitable[int]", redis.lpush("neobank:dead_letter", json.dumps(job))
                    )
                    log.error("job_dead_letter", job_id=job_id)

        except asyncio.CancelledError:
            break
        except Exception as e:
            log.error("worker_error", error=str(e))
            await asyncio.sleep(1)


def main() -> None:
    """Entry point for the ingestion worker."""
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()
