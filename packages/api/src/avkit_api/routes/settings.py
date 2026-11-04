"""Settings GET/PUT by namespace."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from avkit_api.auth import require_bearer
from avkit_api.dependencies import get_settings_service
from avkit_api.schemas.settings import SettingsPutIn
from avkit_core.domain.errors import NotFoundError
from avkit_core.domain.settings import SETTING_NAMESPACES

router = APIRouter(prefix="/settings", dependencies=[Depends(require_bearer)])


def _require_namespace(namespace: str) -> None:
    if namespace not in SETTING_NAMESPACES:
        raise NotFoundError(f"unknown settings namespace {namespace}")


@router.get("/{namespace}")
def get_settings(
    namespace: str,
    settings: Any = Depends(get_settings_service),
) -> dict[str, object]:
    """Return a namespace with defaults filled."""
    _require_namespace(namespace)
    return settings.get_namespace(namespace)


@router.put("/{namespace}")
def put_settings(
    namespace: str,
    body: SettingsPutIn,
    settings: Any = Depends(get_settings_service),
) -> dict[str, object]:
    """Replace provided leaves atomically via `set_namespace`."""
    _require_namespace(namespace)
    mapping = body.model_dump(exclude_unset=True)
    settings.set_namespace(namespace, mapping)
    return settings.get_namespace(namespace)
