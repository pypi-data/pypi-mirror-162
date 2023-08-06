import pytest
import requests
from pandas import DataFrame
from requests import Response

from superwise.models.notification import Notification
from superwise.resources.superwise_enums import NotifyUpon
from superwise.resources.superwise_enums import ScheduleCron


@pytest.fixture(scope="function")
def mock_monitor_get_policy_templates(monkeypatch):
    def mock_monitors_get_templates_logic(*args, **kwargs):
        get_response = Response()
        get_response._content = b"""
            [
          {
            "description": "Scanning the X top important features for long-lasting drift on the entire set level",
            "name": "Feature stability"
          },
          {
            "description": "Scan input drift on the segment level",
            "name": "Dataset shift"
          },
          {
           "description": "Alert when input is above a certain threshold from the baseline",
           "name": "Training-Serving skew"
          },
          {
            "description": "Missing values on a feature level on a segment level",
            "name": "Missing values"
          },
          {
            "description": "Anomaly in % of outliers on a feature level (numeric only)",
            "name": "Out-of-Range"
          },
          {
            "description": "Anomaly in % of new values on a feature level (categorical only)",
            "name": "New values"
          }]
            """
        get_response.status_code = 200
        return get_response

    monkeypatch.setattr(requests, "get", mock_monitors_get_templates_logic)


@pytest.fixture(scope="function")
def mock_empty_monitor_get_policy_templates(monkeypatch):
    def mock_monitors_get_templates_not_templates_logic(*args, **kwargs):
        get_response = Response()
        get_response._content = b""
        get_response.status_code = 200
        return get_response

    monkeypatch.setattr(requests, "get", mock_monitors_get_templates_not_templates_logic)


@pytest.fixture(scope="function")
def mock_bad_response_monitor_get_policy_templates(monkeypatch):
    def mock_monitors_get_templates_not_bad_status_code_logic(*args, **kwargs):
        get_response = Response()
        get_response._content = b"Internal Server Error"
        get_response.status_code = 500
        return get_response

    monkeypatch.setattr(requests, "get", mock_monitors_get_templates_not_bad_status_code_logic)


@pytest.fixture(scope="function")
def mock_monitor_post_create_policy_from_templates(monkeypatch):
    def mock_monitor_create_policy_from_template_logic(*args, **kwargs):
        post_response = Response()
        post_response.status_code = 201
        return post_response

    monkeypatch.setattr(requests, "post", mock_monitor_create_policy_from_template_logic)


def test_get_policy_templates(mock_monitor_get_policy_templates, sw):
    templates = sw.policy.get_policy_templates()
    assert isinstance(templates, DataFrame)
    assert sorted(templates.columns.tolist()) == ["description", "name"]
    assert len(templates) == 6


def test_get_policy_templates_when_no_template(mock_empty_monitor_get_policy_templates, sw):
    with pytest.raises(AssertionError):
        sw.policy.get_policy_templates()


def test_get_policy_templates_when_get_error_response(
    mock_bad_response_monitor_get_policy_templates, sw
):
    with pytest.raises(Exception):
        sw.policy.get_policy_templates()


def test_create_policy_from_template(mock_monitor_post_create_policy_from_templates, sw):
    response = sw.policy.create_policy_from_template(
        model_id=1,
        template_name="template_id",
        policy_name="test policy",
        notification_channels=[Notification(id=1)],
        notify_upon=NotifyUpon.detection_and_resolution,
        schedule=ScheduleCron.EVERY_2ND_MONTH,
    )
    assert response.status_code == 201
