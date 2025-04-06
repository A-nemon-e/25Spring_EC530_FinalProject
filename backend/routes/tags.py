from flask import Blueprint, request, jsonify
from database import get_db

tags_bp = Blueprint("tags", __name__)

# 添加标签（POST /api/tags）
@tags_bp.route("", methods=["POST"])
def create_tag():
    data = request.get_json()
    name = data.get("name")
    category = data.get("category")

    if not name or not category:
        return jsonify({"error": "标签名和分类是必填项"}), 400

    with get_db() as (conn, cursor):
        cursor.execute("INSERT INTO tags (name, category) VALUES (?, ?)", (name, category))
        tag_id = cursor.lastrowid

    return jsonify({"id": tag_id, "name": name, "category": category}), 201
