import pytest
import requests
from requests import Response

from superwise.models.notification import Notification


@pytest.fixture(scope="function")
def mock_notification_requests(monkeypatch):
    get_response = Response()
    get_response._content = b'{"id": 14, "name": "oryan test 123", "type": "Email", "is_enabled": true, "is_hide": false, "created_at": 1647765197, "notification_metadata": {"target": ["oryan.omer@superwise.ai"]}, "last_delivery_status": "Success", "last_delivery_ts": 1647765208}'
    get_response.status_code = 201
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: get_response)
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: get_response)


def test_create_notification(mock_notification_requests, sw):
    notification = sw.notification.create_email_notification(name="oryan test 123", email="oryan.omer@superwise.ai")
    assert isinstance(notification, Notification)
    assert notification.name == "oryan test 123"


def test_get_notification(mock_notification_requests, sw):
    notification = sw.notification.get(name="oryan test 123")
    assert isinstance(notification, Notification)
