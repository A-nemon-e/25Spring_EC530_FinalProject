import os
from flask import Blueprint, request
from werkzeug.utils import secure_filename
from database import get_db
from utils.idgen import generate_uuid
from utils.response import success, error
from datetime import datetime, timezone
import json

files_bp = Blueprint("files", __name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@files_bp.route("/upload", methods=["POST"])
def upload_file():
    """
    上传文件并指定标签和文件夹
    ---
    tags:
      - 文件
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: 要上传的 PDF 文件
      - name: tags
        in: formData
        type: string
        required: false  # ✅ 改为 false
        description: JSON 字符串形式的 tag_id 列表（可选）
      - name: folders
        in: formData
        type: string
        required: false  # ✅ 改为 false
        description: JSON 字符串形式的 folder_id 列表（可选）
    responses:
      201:
        description: 上传成功
    """
    file = request.files.get("file")
    tags_raw = request.form.get("tags")
    folders_raw = request.form.get("folders")

    if not file:
        return error("缺少文件", 400)

    tag_ids = []
    folder_ids = []

    try:
        if tags_raw:
            tag_ids = json.loads(tags_raw)
        if folders_raw:
            folder_ids = json.loads(folders_raw)
    except Exception:
        return error("tags 和 folders 必须是 JSON 数组字符串", 400)

    if not isinstance(tag_ids, list) or not isinstance(folder_ids, list):
        return error("tags 和 folders 格式错误，必须是数组", 400)



    original_name = file.filename
    file_id = generate_uuid()

    # 生成路径
    today = datetime.now(timezone.utc)
    folder_name = today.strftime("%Y_%m")
    folder_path = os.path.join(UPLOAD_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    filename = f"{file_id}.pdf"
    save_path = os.path.join(folder_path, secure_filename(filename))

    try:
        file.save(save_path)
    except Exception as e:
        return error(f"保存文件失败：{str(e)}", 500)

    uploaded_at = today.isoformat()

    try:
        with get_db() as (conn, cursor):
            # 插入 files 表
            cursor.execute("""
                INSERT INTO files (id, name, upload_path, size, uploaded_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                file_id,
                original_name,
                save_path,
                os.path.getsize(save_path),
                uploaded_at
            ))

            # 插入 file_tags
            for tag_id in tag_ids:
                cursor.execute("SELECT id FROM tags WHERE id = ?", (tag_id,))
                if not cursor.fetchone():
                    raise ValueError(f"标签 ID 不存在：{tag_id}")
                cursor.execute("INSERT INTO file_tags (file_id, tag_id) VALUES (?, ?)", (file_id, tag_id))

            # 插入 file_folders
            for folder_id in folder_ids:
                cursor.execute("SELECT id FROM folders WHERE id = ?", (folder_id,))
                if not cursor.fetchone():
                    raise ValueError(f"文件夹 ID 不存在：{folder_id}")
                cursor.execute("INSERT INTO file_folders (file_id, folder_id) VALUES (?, ?)", (file_id, folder_id))

    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        return error(f"数据库写入失败：{str(e)}", 500)

    return success({
        "file_id": file_id,
        "name": original_name,
        "uploaded_at": uploaded_at
    }, code=201)



@files_bp.route("/<file_id>", methods=["GET"])
def get_file(file_id):
    """
    获取单个文件详情
    ---
    tags:
      - 文件
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: 文件 ID
    responses:
      200:
        description: 成功返回文件详情
    """
    with get_db() as (conn, cursor):
        # 查询文件主信息
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        file = cursor.fetchone()
        if not file:
            return error("文件不存在", 404)

        # 查询标签信息
        cursor.execute("""
            SELECT t.id, t.name, t.category
            FROM file_tags ft
            JOIN tags t ON ft.tag_id = t.id
            WHERE ft.file_id = ?
        """, (file_id,))
        tags = [dict(row) for row in cursor.fetchall()]

        # 查询文件夹信息
        cursor.execute("""
            SELECT f.id, f.name, f.parent_id
            FROM file_folders ff
            JOIN folders f ON ff.folder_id = f.id
            WHERE ff.file_id = ?
        """, (file_id,))
        folders = [dict(row) for row in cursor.fetchall()]

        return success({
            "id": file["id"],
            "name": file["name"],
            "size": file["size"],
            "upload_path": file["upload_path"],
            "uploaded_at": file["uploaded_at"],
            "tags": tags,
            "folders": folders
        })

@files_bp.route("/<file_id>", methods=["PUT"])
def update_file_relations(file_id):
    """
    修改文件的标签和文件夹绑定（传空视为清空，必须显式提供不修改部分）
    ---
    tags:
      - 文件
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            tags:
              type: array
              items: { type: string }
            folders:
              type: array
              items: { type: string }
    responses:
      200:
        description: 修改成功
    """
    data = request.get_json()
    tags = data.get("tags")
    folders = data.get("folders")

    if tags is None or folders is None:
        return error("tags 和 folders 都必须提供（可为空数组）", 400)

    if not isinstance(tags, list) or not isinstance(folders, list):
        return error("tags 和 folders 必须是数组", 400)

    with get_db() as (conn, cursor):
        # 检查文件是否存在
        cursor.execute("SELECT id FROM files WHERE id = ?", (file_id,))
        if not cursor.fetchone():
            return error("文件不存在", 404)

        # 清除旧绑定
        cursor.execute("DELETE FROM file_tags WHERE file_id = ?", (file_id,))
        cursor.execute("DELETE FROM file_folders WHERE file_id = ?", (file_id,))

        # 插入新的标签
        for tag_id in tags:
            cursor.execute("SELECT id FROM tags WHERE id = ?", (tag_id,))
            if not cursor.fetchone():
                return error(f"标签不存在：{tag_id}", 400)
            cursor.execute("INSERT INTO file_tags (file_id, tag_id) VALUES (?, ?)", (file_id, tag_id))

        # 插入新的文件夹
        for folder_id in folders:
            cursor.execute("SELECT id FROM folders WHERE id = ?", (folder_id,))
            if not cursor.fetchone():
                return error(f"文件夹不存在：{folder_id}", 400)
            cursor.execute("INSERT INTO file_folders (file_id, folder_id) VALUES (?, ?)", (file_id, folder_id))

    return success({"file_id": file_id}, 200)

@files_bp.route("", methods=["GET"])
def list_files():
    """
    分页获取文件（支持按标签 ID 和文件夹 ID 筛选，返回文件夹完整路径）
    ---
    tags:
      - 文件
    parameters:
      - name: folder_id
        in: query
        type: string
        required: false
      - name: tag_id
        in: query
        type: string
        required: false
      - name: page
        in: query
        type: integer
        required: false
      - name: size
        in: query
        type: integer
        required: false
    responses:
      200:
        description: 文件分页结果，包含标签与文件夹完整路径
    """
    folder_id = request.args.get("folder_id")
    tag_id = request.args.get("tag_id")
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 20))

    if not folder_id and not tag_id:
        return error("必须提供 folder_id 或 tag_id 至少一个筛选条件", 400)

    offset = (page - 1) * size

    with get_db() as (conn, cursor):
        # 构建 JOIN 和 WHERE 子句
        joins = []
        where_clauses = []
        params = []

        if folder_id:
            joins.append("JOIN file_folders ff ON f.id = ff.file_id")
            where_clauses.append("ff.folder_id = ?")
            params.append(folder_id)

        if tag_id:
            joins.append("JOIN file_tags ft ON f.id = ft.file_id")
            where_clauses.append("ft.tag_id = ?")
            params.append(tag_id)

        join_sql = " " + " ".join(joins)
        where_sql = " WHERE " + " AND ".join(where_clauses)

        # 分页主查询
        list_query = f"""
            SELECT f.* FROM files f
            {join_sql}
            {where_sql}
            ORDER BY f.uploaded_at DESC
            LIMIT ? OFFSET ?
        """
        params_with_pagination = params + [size, offset]
        cursor.execute(list_query, params_with_pagination)
        files = cursor.fetchall()

        # 查询总数
        count_query = f"""
            SELECT COUNT(DISTINCT f.id) FROM files f
            {join_sql}
            {where_sql}
        """
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # 预加载所有文件夹用于路径构建
        cursor.execute("SELECT id, name, parent_id FROM folders")
        all_folders = cursor.fetchall()
        folder_dict = {f["id"]: dict(f) for f in all_folders}

        def build_full_path(folder_id):
            path = []
            while folder_id and folder_id in folder_dict:
                folder = folder_dict[folder_id]
                path.insert(0, folder["name"])
                folder_id = folder["parent_id"]
            return path

        # 构建文件列表结果
        result = []
        for f in files:
            file_id = f["id"]

            # 查标签
            cursor.execute("""
                SELECT t.id, t.name, t.category
                FROM file_tags ft JOIN tags t ON ft.tag_id = t.id
                WHERE ft.file_id = ?
            """, (file_id,))
            tags = [dict(row) for row in cursor.fetchall()]

            # 查文件夹 + 构造 full_path
            cursor.execute("""
                SELECT fo.id, fo.name, fo.parent_id
                FROM file_folders ff JOIN folders fo ON ff.folder_id = fo.id
                WHERE ff.file_id = ?
            """, (file_id,))
            raw_folders = cursor.fetchall()

            folders = []
            for row in raw_folders:
                folder = dict(row)
                folder["full_path"] = build_full_path(folder["id"])
                folders.append(folder)

            result.append({
                "id": file_id,
                "name": f["name"],
                "size": f["size"],
                "upload_path": f["upload_path"],
                "uploaded_at": f["uploaded_at"],
                "tags": tags,
                "folders": folders
            })

    return success({
        "total": total,
        "files": result
    })


@files_bp.route("/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    """
    删除文件及其所有关联
    ---
    tags:
      - 文件
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: 要删除的文件 ID
    responses:
      200:
        description: 删除成功
    """
    with get_db() as (conn, cursor):
        # 1. 查找文件是否存在
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        file = cursor.fetchone()
        if not file:
            return error("文件不存在", 404)

        upload_path = file["upload_path"]

        # 2. 删除本地文件
        if upload_path and os.path.exists(upload_path):
            try:
                os.remove(upload_path)
            except Exception as e:
                return error(f"本地文件删除失败：{str(e)}", 500)

        # 3. 删除中间表中的所有绑定
        cursor.execute("DELETE FROM file_tags WHERE file_id = ?", (file_id,))
        cursor.execute("DELETE FROM file_folders WHERE file_id = ?", (file_id,))

        # 4. 删除文件主记录
        cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))

    return success({"deleted_file_id": file_id}, 200)

