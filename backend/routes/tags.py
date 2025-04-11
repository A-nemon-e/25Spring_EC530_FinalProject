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
            name_clean = name.strip()
            category_clean = category.strip()

            # 1. 检查是否已经是主标签
            cursor.execute("SELECT id FROM tags WHERE name = ? AND category = ?", (name_clean, category_clean))
            existing = cursor.fetchone()
            if existing:
                return error("标签已存在", 409)

            # 2. 检查是否与任意 alias 冲突（任何标签下）
            cursor.execute("SELECT id FROM tag_aliases WHERE alias = ?", (name_clean,))
            alias_conflict = cursor.fetchone()
            if alias_conflict:
                return error("该标签名已作为别名存在", 409)

            # 3. 插入
            cursor.execute(
                "INSERT INTO tags (name, category) VALUES (?, ?)",
                (name_clean, category_clean)
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
                    # cursor.execute("SELECT alias FROM tag_aliases WHERE tag_id = ?", (tag["id"],))
                    # aliases = [row["alias"] for row in cursor.fetchall()]
                    cursor.execute("SELECT id, alias FROM tag_aliases WHERE tag_id = ?", (tag["id"],))
                    aliases = [{"id": row["id"], "name": row["alias"]} for row in cursor.fetchall()]

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

@tags_bp.route("/<int:tag_id>/alias", methods=["POST"])
def add_alias(tag_id):
    """
    给指定标签添加别名
    ---
    tags:
      - 标签
    parameters:
      - name: tag_id
        in: path
        type: integer
        required: true
        description: 标签 ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            alias:
              type: string
              example: 老肖
    responses:
      201:
        description: 添加成功
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
                tag_id:
                  type: integer
                alias:
                  type: string
    """
    data = request.get_json()
    alias = data.get("alias", "").strip()

    if not alias:
        return error("alias 是必填字段", 400)

    with get_db() as (conn, cursor):
        # 检查标签是否存在
        cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
        tag = cursor.fetchone()
        if not tag:
            return error("指定的标签不存在", 404)

        # 检查是否已存在此 alias（任何标签下）
        cursor.execute("SELECT * FROM tag_aliases WHERE alias = ?", (alias,))
        existing = cursor.fetchone()
        if existing:
            return error("该别名已被占用", 409)

        # 插入别名
        cursor.execute("INSERT INTO tag_aliases (tag_id, alias) VALUES (?, ?)", (tag_id, alias))

    return success({
        "tag_id": tag_id,
        "alias": alias
    }, code=201)


@tags_bp.route("/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    """
    删除主标签（及其所有别名）
    ---
    tags:
      - 标签
    parameters:
      - name: tag_id
        in: path
        type: integer
        required: true
        description: 要删除的标签 ID
    responses:
      200:
        description: 删除成功
    """
    with get_db() as (conn, cursor):
        cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
        tag = cursor.fetchone()
        if not tag:
            return error("标签不存在", 404)

        # 删除主标签（别名表设置外键自动删除 或手动删除都可）
        cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        cursor.execute("DELETE FROM tag_aliases WHERE tag_id = ?", (tag_id,))

    return success({"deleted_tag_id": tag_id}, 200)

@tags_bp.route("/alias/<int:alias_id>", methods=["DELETE"])
def delete_alias(alias_id):
    """
    删除标签别名
    ---
    tags:
      - 标签
    parameters:
      - name: alias_id
        in: path
        type: integer
        required: true
        description: 要删除的别名 ID
    responses:
      200:
        description: 删除成功
    """
    with get_db() as (conn, cursor):
        cursor.execute("SELECT * FROM tag_aliases WHERE id = ?", (alias_id,))
        alias = cursor.fetchone()
        if not alias:
            return error("别名不存在", 404)

        cursor.execute("DELETE FROM tag_aliases WHERE id = ?", (alias_id,))

    return success({"deleted_alias_id": alias_id}, 200)

