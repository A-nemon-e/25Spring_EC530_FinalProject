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



