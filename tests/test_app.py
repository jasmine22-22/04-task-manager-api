import pytest

from app import app, init_db


@pytest.fixture
def client(tmp_path):
    app.config.update(
        TESTING=True,
        DATABASE=str(tmp_path / "tasks.db"),
    )
    init_db()
    return app.test_client()


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={"title": "Write tests", "description": "Cover the API", "done": False},
    )

    assert response.status_code == 201
    assert response.json["title"] == "Write tests"
    assert response.json["description"] == "Cover the API"
    assert response.json["done"] is False


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        ({"description": "Missing title"}, "Title is required"),
        ({"title": "Invalid done", "done": "false"}, "done must be a boolean"),
    ],
)
def test_create_rejects_invalid_data(client, payload, error):
    response = client.post("/tasks", json=payload)

    assert response.status_code == 400
    assert response.json == {"error": error}


def test_get_all_tasks(client):
    client.post("/tasks", json={"title": "Open", "done": False})
    client.post("/tasks", json={"title": "Done", "done": True})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert [task["title"] for task in response.json] == ["Open", "Done"]


def test_get_one_task_and_missing_id(client):
    created = client.post("/tasks", json={"title": "Find me"}).json

    response = client.get(f"/tasks/{created['id']}")
    missing = client.get("/tasks/999")

    assert response.status_code == 200
    assert response.json["title"] == "Find me"
    assert missing.status_code == 404


def test_update_task(client):
    created = client.post("/tasks", json={"title": "Old title"}).json

    response = client.put(
        f"/tasks/{created['id']}",
        json={"title": "New title", "description": "Updated", "done": True},
    )

    assert response.status_code == 200
    assert response.json["title"] == "New title"
    assert response.json["description"] == "Updated"
    assert response.json["done"] is True


def test_delete_task_and_missing_id(client):
    created = client.post("/tasks", json={"title": "Remove me"}).json

    response = client.delete(f"/tasks/{created['id']}")
    missing = client.delete("/tasks/999")

    assert response.status_code == 200
    assert missing.status_code == 404


@pytest.mark.parametrize(
    ("filter_value", "expected"),
    [
        ("true", [True]),
        ("false", [False]),
        ("yes", None),
    ],
)
def test_done_filter(client, filter_value, expected):
    client.post("/tasks", json={"title": "Open", "done": False})
    client.post("/tasks", json={"title": "Done", "done": True})

    response = client.get("/tasks", query_string={"done": filter_value})

    if expected is None:
        assert response.status_code == 400
        assert response.json == {"error": "done must be true or false"}
    else:
        assert response.status_code == 200
        assert [bool(task["done"]) for task in response.json] == expected