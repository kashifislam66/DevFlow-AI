import json, logging, time
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger("devflow")

# Console pe JSON lines
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def log_event(event: str, **fields: Any) -> None:
    """Ek structured log line (JSON)."""
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, default=str, ensure_ascii=False))


@contextmanager
def node_timer(node: str, thread_id: str | None = None, **extra: Any):
    """Node start/end + duration_ms automatic."""
    log_event("node_started", node=node, thread_id=thread_id, **extra)
    t0 = time.time()
    try:
        yield
        log_event(
            "node_completed",
            node=node,
            thread_id=thread_id,
            duration_ms=int((time.time() - t0) * 1000),
            status="ok",
            **extra,
        )
    except Exception as e:
        log_event(
            "node_failed",
            node=node,
            thread_id=thread_id,
            duration_ms=int((time.time() - t0) * 1000),
            status="error",
            error=str(e),
            **extra,
        )
        raise