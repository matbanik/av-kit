"""A quiet progress bar that hands `hf_hub_download`'s byte count to a fraction callback.

huggingface_hub builds a class it does not own as `cls(**kwargs)` and leaves it enabled, on the
HTTP path and on the Xet path. Defining `update_transfer` makes the Xet path keep one bar (the
bytes written to disk) instead of two, so the reported fraction never jumps between bars.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from tqdm import tqdm


class _NullSink:
    """Where the bar's text goes: nowhere. The backend has no console to draw on."""

    def write(self, _text: str) -> int:
        return 0

    def flush(self) -> None:
        return None


def progress_bar_class(on_progress: Callable[[float], None]) -> type[tqdm]:  # type: ignore[type-arg]
    """A tqdm subclass whose every update reports `n / total`, capped at 1.0 and never lower."""

    class _ReportingBar(tqdm):  # type: ignore[type-arg]
        monitor_interval = 0  # no monitor thread

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            kwargs.pop("name", None)
            kwargs["disable"] = False
            kwargs["file"] = _NullSink()
            self._reported = 0.0
            super().__init__(*args, **kwargs)

        def update(self, n: float | None = 1) -> bool | None:
            shown = super().update(n)
            total = self.total
            if total:
                fraction = min(float(self.n) / float(total), 1.0)
                if fraction > self._reported:
                    self._reported = fraction
                    on_progress(fraction)
            return shown

        def update_transfer(self, n: float | None = 1) -> None:
            del n

        def set_transfer_postfix_str(self, s: str = "", refresh: bool = True) -> None:
            del s, refresh

    return _ReportingBar
