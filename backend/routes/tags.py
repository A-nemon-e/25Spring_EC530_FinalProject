from flask import Blueprint, request
from database import get_db
from utils.response import success, error

tags_bp = Blueprint("tags", __name__)

@tags_bp.route("", methods=["POST"]) # /api/tags
def create_tag():
    data = request.get_json()
    name = data.get("name")
    category = data.get("category")

    if not name or not category:
        return error("标签名（name）和分类（category）是必填字段", 400)

    try:
        with get_db() as (conn, cursor):
            cursor.execute(
                "INSERT INTO tags (name, category) VALUES (?, ?)",
                (name.strip(), category.strip())
            )
            tag_id = cursor.lastrowid
    except Exception as e:
        return error(f"数据库写入失败：{str(e)}", 500)

    return success({
        "id": tag_id,
        "name": name,
        "category": category
    }, code=201)
