# Task Manager API

A REST API for managing tasks, built with Flask and SQLite.

## Run

From this directory:

```bash
pip install -r requirements.txt
python app.py
```

The server runs at [http://localhost:5000](http://localhost:5000).

## Docker

```bash
docker build -t task-manager-api .
docker run -p 5000:5000 task-manager-api
```

Data is stored inside the container and is lost when the container is removed.

## Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/tasks` | Create a task. |
| `GET` | `/tasks` | List tasks, optionally filtered by completion status. |
| `GET` | `/tasks/<task_id>` | Retrieve one task. |
| `PUT` | `/tasks/<task_id>` | Update a task. |
| `DELETE` | `/tasks/<task_id>` | Delete a task. |

`GET /tasks?done=true` returns completed tasks; `GET /tasks?done=false` returns incomplete tasks. Any other `done` value returns `400` with `{"error": "done must be true or false"}`.

## Examples

Create a task:

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Prepare report","description":"Draft the monthly report","done":false}'
```

List completed tasks:

```bash
curl "http://localhost:5000/tasks?done=true"
```

## Validation and errors

Creating or updating a task requires a non-empty string `title`. The optional `done` field must be a JSON boolean. Invalid input returns `400` with an error message. Requests for a task ID that does not exist return `404` for `GET`, `PUT`, and `DELETE`.

## Run tests

Run `python -m pytest` from this directory. The suite contains 10 test cases.