from flask import Blueprint, request
from database import get_db
from utils.response import success, error

tags_bp = Blueprint("tags", __name__)

@tags_bp.route("", methods=["POST"]) # /api/tags

def create_tag():
    """
    添加新标签
    ---
    tags:
      - 标签
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: 老肖
            category:
              type: string
              example: 作曲家
    responses:
      201:
        description: 成功添加标签
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            code:
              type: integer
              example: 201
            data:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                category:
                  type: string
            error:
              type: string
              example: null
    """
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
