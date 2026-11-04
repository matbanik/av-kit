"""Shared extract mutex and TTL cache for YouTubePort calls."""

from __future__ import annotations

import threading
import time

from avkit_core.domain.download import PlaylistInfo, VideoInfo
from avkit_core.ports.youtube import YouTubePort

EXTRACT_CACHE_TTL_S = 300.0


class ExtractCoordinator:
    """One in-flight extract across download and transcript services."""

    def __init__(self, youtube: YouTubePort, ttl_s: float = EXTRACT_CACHE_TTL_S) -> None:
        self._youtube = youtube
        self._ttl_s = ttl_s
        self._lock = threading.Lock()
        self._info_cache: dict[str, tuple[float, VideoInfo | PlaylistInfo]] = {}
        self._ids_cache: dict[str, tuple[float, list[str]]] = {}
        self.in_flight = 0
        self.max_in_flight = 0

    def _enter(self) -> None:
        self.in_flight += 1
        if self.in_flight > self.max_in_flight:
            self.max_in_flight = self.in_flight

    def _leave(self) -> None:
        self.in_flight -= 1

    def extract_info(self, url: str, flat: bool = False) -> VideoInfo | PlaylistInfo:
        key = url.strip()
        now = time.monotonic()
        with self._lock:
            cached = self._info_cache.get(key)
            if cached is not None and now - cached[0] < self._ttl_s:
                return cached[1]
            self._enter()
            try:
                result = self._youtube.extract_info(key, flat=flat)
                self._info_cache[key] = (time.monotonic(), result)
                return result
            finally:
                self._leave()

    def extract_video_ids(self, channel_url: str) -> list[str]:
        key = channel_url.strip()
        now = time.monotonic()
        with self._lock:
            cached = self._ids_cache.get(key)
            if cached is not None and now - cached[0] < self._ttl_s:
                return list(cached[1])
            self._enter()
            try:
                result = self._youtube.extract_video_ids(key)
                self._ids_cache[key] = (time.monotonic(), list(result))
                return list(result)
            finally:
                self._leave()
