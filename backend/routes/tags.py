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
            cursor.execute("SELECT id FROM tags WHERE name = ? AND category = ?", (name.strip(), category.strip()))
            existing = cursor.fetchone()
            if existing:
                return error("标签已存在", 409)

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

@tags_bp.route("", methods=["GET"])  # /api/tags?q=xxx
def get_tags():
    """
    获取标签（可按关键词查询）
    ---
    tags:
      - 标签
    parameters:
      - name: q
        in: query
        type: string
        required: false
        description: 标签名或别名（可选）
    responses:
      200:
        description: 标签信息（包括别名）
        schema:
          type: object
          properties:
            status:
              type: string
            code:
              type: integer
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  category:
                    type: string
                  aliases:
                    type: array
                    items:
                      type: string
    """
    query = request.args.get("q")

    with get_db() as (conn, cursor):
        if query:
            q = query.strip()

            # 尝试匹配主标签名
            cursor.execute("SELECT * FROM tags WHERE name LIKE ?", (f"%{q}%",))
            tags = cursor.fetchall()

            if tags:
                # 找到主标签，查出所有别名
                result = []
                for tag in tags:
                    cursor.execute("SELECT alias FROM tag_aliases WHERE tag_id = ?", (tag["id"],))
                    aliases = [row["alias"] for row in cursor.fetchall()]
                    result.append({
                        "id": tag["id"],
                        "name": tag["name"],
                        "category": tag["category"],
                        "aliases": aliases
                    })
                return success(result)

            # 否则查 alias 表
            cursor.execute("SELECT * FROM tag_aliases WHERE alias LIKE ?", (f"%{q}%",))
            alias_row = cursor.fetchone()
            if alias_row:
                tag_id = alias_row["tag_id"]
                cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
                tag = cursor.fetchone()
                cursor.execute("SELECT alias FROM tag_aliases WHERE tag_id = ?", (tag_id,))
                aliases = [row["alias"] for row in cursor.fetchall()]
                return success([{
                    "id": tag["id"],
                    "name": tag["name"],
                    "category": tag["category"],
                    "aliases": aliases
                }])

            # 都没找到
            return success([])

        else:
            # 不传 q，返回所有主标签（不含 alias）
            cursor.execute("SELECT * FROM tags ORDER BY id DESC")
            tags = cursor.fetchall()
            result = []
            for tag in tags:
                cursor.execute("SELECT alias FROM tag_aliases WHERE tag_id = ?", (tag["id"],))
                aliases = [row["alias"] for row in cursor.fetchall()]
                result.append({
                    "id": tag["id"],
                    "name": tag["name"],
                    "category": tag["category"],
                    "aliases": aliases
                })
            return success(result)
