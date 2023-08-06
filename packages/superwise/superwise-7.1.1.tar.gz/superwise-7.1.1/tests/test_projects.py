import pytest
import requests
from requests import Response

from superwise.models.project import Project


@pytest.fixture(scope="function")
def mock_project_requests(monkeypatch):
    get_response = Response()
    get_response._content = b'{"id": 1, "name": "super cool project", "description": "here we have the most amazing project", "created_at": "2022-05-02T16:10:45.318683", "created_by": "me"}'
    get_response.status_code = 201

    delete_response = Response()
    delete_response._content = b"1"
    delete_response.status_code = 201

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: get_response)
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: get_response)
    monkeypatch.setattr(requests, "delete", lambda *args, **kwargs: delete_response)


@pytest.fixture(scope="function")
def mock_multi_project_requests(monkeypatch):
    get_response = Response()
    get_response._content = b'[{"id": 1, "name": "super cool project", "description": "here we have the most amazing project", "created_at": "2022-05-02T16:10:45.318683", "created_by": "me"},{"id": 1, "name": "super cool project", "description": "here we have the most amazing project", "created_at": "2022-05-02T16:10:45.318683", "created_by": "me"} ]'
    get_response.status_code = 201

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: get_response)


def test_create_project(mock_project_requests, sw):
    p = Project(name="super cool project", description="here we have the most amazing project")
    response = sw.project.create(p)
    assert response.id == 1 and response.name == p.name


def test_delete_project(mock_project_requests, sw):
    project = Project(id=1, name="super cool project", description="here we have the most amazing project")
    res = sw.project.delete(project)
    assert res.status_code == 201
    assert res.json() in [project.id, f"{project.id}"]


def test_get_project_by_id(mock_project_requests, sw):
    project = Project(id=1, name="super cool project", description="here we have the most amazing project")
    ret_project = sw.project.get_by_id(project.id)
    assert isinstance(ret_project, Project)
    assert project.name == ret_project.name


def test_get_project_by_name(mock_multi_project_requests, sw):
    project = Project(id=1, name="super cool project", description="here we have the most amazing project")
    projects = sw.project.get_by_name(project.name)
    assert len(projects) == 2
