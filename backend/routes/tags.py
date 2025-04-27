from flask import Blueprint, request
from database import get_db
from utils.response import success, error

tags_bp = Blueprint("tags", __name__)

@tags_bp.route("", methods=["POST"]) # /api/tags
def create_tag():
    """
    Add a new tag.
    ---
    tags:
      - Tag
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Lao Xiao
            category:
              type: string
              example: Composer
    responses:
      201:
        description: Tag added successfully
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
        return error("Name and category are required fields", 400)

    try:
        with get_db() as (conn, cursor):
            name_clean = name.strip()
            category_clean = category.strip()

            # 1. Check if the tag already exists as a main tag
            cursor.execute("SELECT id FROM tags WHERE name = ? AND category = ?", (name_clean, category_clean))
            existing = cursor.fetchone()
            if existing:
                return error("Tag already exists", 409)

            # 2. Check if there is a conflict with any alias
            cursor.execute("SELECT id FROM tag_aliases WHERE alias = ?", (name_clean,))
            alias_conflict = cursor.fetchone()
            if alias_conflict:
                return error("This name already exists as an alias", 409)

            # 3. Insert new tag
            cursor.execute(
                "INSERT INTO tags (name, category) VALUES (?, ?)",
                (name_clean, category_clean)
            )
            tag_id = cursor.lastrowid

    except Exception as e:
        return error(f"Database write failed: {str(e)}", 500)

    return success({
        "id": tag_id,
        "name": name,
        "category": category
    }, code=201)

@tags_bp.route("", methods=["GET"])  # /api/tags?q=xxx
def get_tags():
    """
    Retrieve tags (optional keyword search).
    ---
    tags:
      - Tag
    parameters:
      - name: q
        in: query
        type: string
        required: false
        description: Tag name or alias (optional)
    responses:
      200:
        description: Tag information (including aliases)
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

            # Try to match main tag name
            cursor.execute("SELECT * FROM tags WHERE name LIKE ?", (f"%{q}%",))
            tags = cursor.fetchall()

            if tags:
                result = []
                for tag in tags:
                    cursor.execute("SELECT id, alias FROM tag_aliases WHERE tag_id = ?", (tag["id"],))
                    aliases = [{"id": row["id"], "name": row["alias"]} for row in cursor.fetchall()]

                    result.append({
                        "id": tag["id"],
                        "name": tag["name"],
                        "category": tag["category"],
                        "aliases": aliases
                    })
                return success(result)

            # Otherwise search in aliases
            cursor.execute("SELECT * FROM tag_aliases WHERE alias LIKE ?", (f"%{q}%",))
            alias_rows = cursor.fetchall()

            if alias_rows:
                result = []
                seen_tag_ids = set()

                for alias in alias_rows:
                    tag_id = alias["tag_id"]
                    if tag_id in seen_tag_ids:
                        continue  # Remove duplicates
                    seen_tag_ids.add(tag_id)

                    cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
                    tag = cursor.fetchone()
                    if tag:
                        cursor.execute("SELECT id, alias FROM tag_aliases WHERE tag_id = ?", (tag_id,))
                        aliases = [{"id": row["id"], "name": row["alias"]} for row in cursor.fetchall()]
                        result.append({
                            "id": tag["id"],
                            "name": tag["name"],
                            "category": tag["category"],
                            "aliases": aliases
                        })

                return success(result)

            # No matches found
            return success([])

        else:
            # No keyword provided, return all main tags
            cursor.execute("SELECT * FROM tags ORDER BY id DESC")
            tags = cursor.fetchall()
            result = []
            for tag in tags:
                cursor.execute("SELECT id, alias FROM tag_aliases WHERE tag_id = ?", (tag["id"],))
                aliases = [{"id": row["id"], "name": row["alias"]} for row in cursor.fetchall()]
                
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
    Add an alias to a specified tag.
    ---
    tags:
      - Tag
    parameters:
      - name: tag_id
        in: path
        type: integer
        required: true
        description: Tag ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            alias:
              type: string
              example: Lao Xiao
    responses:
      201:
        description: Alias added successfully
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
        return error("Alias is a required field", 400)

    with get_db() as (conn, cursor):
        # Check if the tag exists
        cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
        tag = cursor.fetchone()
        if not tag:
            return error("The specified tag does not exist", 404)

        # Check if alias already exists
        cursor.execute("SELECT * FROM tag_aliases WHERE alias = ?", (alias,))
        existing = cursor.fetchone()
        if existing:
            return error("This alias already exists", 409)

        # Insert the alias
        cursor.execute("INSERT INTO tag_aliases (tag_id, alias) VALUES (?, ?)", (tag_id, alias))

    return success({
        "tag_id": tag_id,
        "alias": alias
    }, code=201)

@tags_bp.route("/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    """
    Delete a main tag (along with all its aliases).
    ---
    tags:
      - Tag
    parameters:
      - name: tag_id
        in: path
        type: integer
        required: true
        description: Tag ID to delete
    responses:
      200:
        description: Deletion successful
    """
    with get_db() as (conn, cursor):
        cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
        tag = cursor.fetchone()
        if not tag:
            return error("Tag not found", 404)

        # Delete main tag (and its aliases)
        cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        cursor.execute("DELETE FROM tag_aliases WHERE tag_id = ?", (tag_id,))

    return success({"deleted_tag_id": tag_id}, 200)

@tags_bp.route("/alias/<int:alias_id>", methods=["DELETE"])
def delete_alias(alias_id):
    """
    Delete a tag alias.
    ---
    tags:
      - Tag
    parameters:
      - name: alias_id
        in: path
        type: integer
        required: true
        description: Alias ID to delete
    responses:
      200:
        description: Deletion successful
    """
    with get_db() as (conn, cursor):
        cursor.execute("SELECT * FROM tag_aliases WHERE id = ?", (alias_id,))
        alias = cursor.fetchone()
        if not alias:
            return error("Alias not found", 404)

        cursor.execute("DELETE FROM tag_aliases WHERE id = ?", (alias_id,))

    return success({"deleted_alias_id": alias_id}, 200)
