"""Session 106 (MEU-174, AC-174.9): the `app.update_interval` leaf through `PUT /settings/app`.

The API client of `tests/e2e/test_api_health_settings.py`, with the real `SettingsService`
over the fake unit of work of `tests/unit/test_services.py`, so the core registry decides.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from tests.e2e.test_api_health_settings import AUTH, TOKENS, FakeHealth, _Lifecycle
from tests.unit.test_services import FakeUnitOfWork, SharedFakeFactory

from avkit_api.main import create_app
from avkit_api.wiring import AppServices
from avkit_core.services.settings import SettingsService

URL = "/api/v1/settings/app"


def _client() -> TestClient:
    life = _Lifecycle()
    services = AppServices(
        download=life,
        transcript=life,
        tts=life,
        models=life,
        settings=SettingsService(SharedFakeFactory(FakeUnitOfWork())),
        health=FakeHealth(),
        conversion=life,
        capture=life,
    )
    return TestClient(create_app(tokens=TOKENS, services=services, engine_dispose=None))


def _stored(client: TestClient) -> object:
    response = client.get(URL, headers=AUTH)
    assert response.status_code == 200
    return response.json().get("update_interval")


def test_ac_174_9_default_is_weekly() -> None:
    assert _stored(_client()) == "weekly"


def test_ac_174_9_put_accepts_the_three_wires() -> None:
    client = _client()
    for wire in ("monthly", "never", "weekly"):
        response = client.put(URL, headers=AUTH, json={"update_interval": wire})
        assert response.status_code == 200, response.text
        assert _stored(client) == wire


@pytest.mark.parametrize(
    "body",
    [
        {"update_interval": "daily"},
        {"update_interval": "Weekly"},
        {"update_interval": 7},
        {"update_intervals": "monthly"},
    ],
)
def test_ac_174_9_put_refuses_other_values_and_keeps_the_stored_one(
    body: dict[str, object],
) -> None:
    client = _client()
    accepted = client.put(URL, headers=AUTH, json={"update_interval": "monthly"})
    assert accepted.status_code == 200, accepted.text
    refused = client.put(URL, headers=AUTH, json=body)
    assert refused.status_code == 422, refused.text
    assert _stored(client) == "monthly"
