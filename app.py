from pathlib import Path
import os
import sqlite3

from flask import Flask, jsonify, request
from werkzeug.serving import run_simple

app = Flask(__name__)
app.config["DATABASE"] = str(Path(__file__).resolve().with_name("tasks.db"))


def get_db():
    return sqlite3.connect(app.config["DATABASE"])


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            done BOOLEAN NOT NULL CHECK (done IN (0, 1))
        )
        """
    )
    db.commit()
    db.close()


@app.route("/tasks", methods=["GET"])
def get_tasks():
    done_filter = request.args.get("done")
    if done_filter is not None and done_filter not in {"true", "false"}:
        return jsonify({"error": "done must be true or false"}), 400

    db = get_db()
    db.row_factory = sqlite3.Row
    if done_filter is None:
        tasks = db.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    else:
        done = done_filter == "true"
        tasks = db.execute(
            "SELECT * FROM tasks WHERE done = ? ORDER BY id", (int(done),)
        ).fetchall()
    db.close()
    return jsonify([dict(task) for task in tasks])


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    db = get_db()
    db.row_factory = sqlite3.Row
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    db.close()
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(dict(task))


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("title"), str)
        or not data["title"].strip()
    ):
        return jsonify({"error": "Title is required"}), 400

    done = data.get("done", False)
    if not isinstance(done, bool):
        return jsonify({"error": "done must be a boolean"}), 400

    title = data["title"]
    description = data.get("description", "")
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, done) VALUES (?, ?, ?)",
        (title, description, int(done)),
    )
    db.commit()
    new_id = cursor.lastrowid
    db.close()
    return jsonify({
        "id": new_id,
        "title": title,
        "description": description,
        "done": done,
    }), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True)
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("title"), str)
        or not data["title"].strip()
    ):
        return jsonify({"error": "Title is required"}), 400

    done = data.get("done", False)
    if not isinstance(done, bool):
        return jsonify({"error": "done must be a boolean"}), 400

    title = data["title"]
    description = data.get("description", "")
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE tasks SET title = ?, description = ?, done = ? WHERE id = ?",
        (title, description, int(done), task_id),
    )
    db.commit()
    updated = cursor.rowcount
    db.close()
    if not updated:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "id": task_id,
        "title": title,
        "description": description,
        "done": done,
    })


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = get_db()
    cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    deleted = cursor.rowcount
    db.close()
    if not deleted:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": "Task deleted successfully"})


if __name__ == "__main__":
    init_db()
    host = os.environ.get("HOST", "localhost")
    run_simple(host, 5000, app)