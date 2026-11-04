"""Shared API models, including the extra-forbid base and error envelope."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    """Request/response base: unknown fields are rejected."""

    model_config = ConfigDict(extra="forbid")


class ErrorBody(ApiModel):
    """Inner `error` object of `ERROR_ENVELOPE`."""

    code: str
    message: str
    details: dict[str, object] | None = None


class ErrorEnvelope(ApiModel):
    """Canonical error payload."""

    error: ErrorBody


class QueueRuntimeOut(ApiModel):
    """Processor snapshot attached to list envelopes."""

    state: str
    current_job_id: str | None = Field(default=None)


class EmptyIn(ApiModel):
    """Body for POST/PUT routes that take no fields. Extra keys are 422."""
