from flask import Blueprint, jsonify, request

from services.tasks import (
    DEFAULT_PRIORITY,
    create_task,
    get_task,
    list_tasks,
    update_task,
)
from services.users import get_user
from utils.errors import AppError

api = Blueprint("api", __name__)

@api.errorhandler(AppError)
def handle_app_error(e):
    return jsonify({"error": e.message}), e.status_code

@api.route("/tasks/<int:task_id>", methods=["GET"])
def get_task_route(task_id):
    return jsonify(get_task(task_id))

@api.route("/tasks", methods=["POST"])
def create_task_route():
    data = request.get_json()
    return jsonify(create_task(data["title"], data["user_id"],
                               data.get("priority", DEFAULT_PRIORITY))), 201

@api.route("/tasks", methods=["GET"])
def list_tasks_route():
    return jsonify(list_tasks(request.args.get("priority"), request.args.get("sort")))

@api.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task_route(task_id):
    return jsonify(update_task(task_id, request.get_json(silent=True)))

@api.route("/users/<int:user_id>", methods=["GET"])
def get_user_route(user_id):
    return jsonify(get_user(user_id))
