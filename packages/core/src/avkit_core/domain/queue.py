"""Session queue runtime (not persistable)."""

from __future__ import annotations

from dataclasses import dataclass

from avkit_core.domain.enums import QueueProcessorState
from avkit_core.domain.errors import ValidationError, require_non_empty_str, require_optional_str

QUEUE_NAMES: frozenset[str] = frozenset({"downloads", "transcripts", "conversions"})
QUEUE_RUNTIME_FIELDS: tuple[str, ...] = ("queue_name", "state", "current_job_id")


@dataclass(frozen=True)
class QueueRuntime:
    """In-memory processor state for one module queue."""

    queue_name: str
    state: QueueProcessorState
    current_job_id: str | None

    def __post_init__(self) -> None:
        require_non_empty_str(self.queue_name, "queue_name")
        if self.queue_name not in QUEUE_NAMES:
            raise ValidationError("queue_name must be one of QUEUE_NAMES")
        if not isinstance(self.state, QueueProcessorState):
            raise ValidationError("state must be a QueueProcessorState")
        require_optional_str(self.current_job_id, "current_job_id")
