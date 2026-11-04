"""Setup-only fakes for the MEU-62 collaborators (`FIXTURE_REPAIRS`, Session 27 plan).

`TtsAssetPort` and the download-runtime reader became required keyword arguments of
`HealthService`, `TTSService` and `ModelService`. Pre-existing tests get these fakes, which
report every asset `ready`, so each existing assertion runs against unchanged behaviour.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from avkit_core.domain.tts import AssetState, ModelDownloadRuntime, TtsAsset


class FakeAssets:
    """`TtsAssetPort` fake; every asset is `ready` unless a test overrides `states`."""

    def __init__(self) -> None:
        self.states: dict[TtsAsset, AssetState] = {asset: AssetState.READY for asset in TtsAsset}
        self.downloads: list[TtsAsset] = []

    def state(self, asset: TtsAsset, models_dir: Path) -> AssetState:
        del models_dir
        return self.states[asset]

    def version(self, asset: TtsAsset, models_dir: Path) -> str | None:
        del asset, models_dir
        return None

    def download(
        self,
        asset: TtsAsset,
        models_dir: Path,
        on_progress: Callable[[float], None],
    ) -> Path:
        self.downloads.append(asset)
        on_progress(1.0)
        self.states[asset] = AssetState.READY
        return models_dir

    def activate(self, models_dir: Path) -> None:
        del models_dir


def idle_runtime() -> ModelDownloadRuntime:
    """The runtime a HealthService reads when no download is in flight."""
    return ModelDownloadRuntime(
        variant_id=None, asset=None, state="Idle", fraction=0.0, error_message=None
    )
