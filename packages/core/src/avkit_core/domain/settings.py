"""Settings namespace/leaf keys and value types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from avkit_core.domain.enums import SettingValueType
from avkit_core.domain.errors import (
    ValidationError,
    require_datetime,
    require_enum,
    require_non_empty_str,
)

SETTING_NAMESPACES: frozenset[str] = frozenset(
    {"downloader", "transcript", "tts", "app", "ui", "converter", "capture"}
)


@dataclass(frozen=True)
class Setting:
    """One persisted settings leaf. Key is never a dotted namespace.path."""

    namespace: str
    key: str
    value: str
    value_type: SettingValueType
    updated_at: datetime

    def __post_init__(self) -> None:
        require_non_empty_str(self.namespace, "namespace")
        if self.namespace not in SETTING_NAMESPACES:
            raise ValidationError("namespace must be one of SETTING_NAMESPACES")
        require_non_empty_str(self.key, "key")
        if "." in self.key:
            raise ValidationError("key must be a leaf name without '.'")
        if not isinstance(self.value, str):
            raise ValidationError("value must be a serialized str")
        require_enum(self.value_type, SettingValueType, "value_type")
        require_datetime(self.updated_at, "updated_at")
