import os
from flask import Blueprint, request
from werkzeug.utils import secure_filename
from database import get_db
from utils.idgen import generate_uuid
from utils.response import success, error
from datetime import datetime, timezone

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

files_bp = Blueprint("files", __name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB 限制

@files_bp.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return error("缺少文件", 400)

    if not file.filename.lower().endswith(".pdf"):
        return error("只允许上传 PDF 文件", 400)

    file.seek(0, os.SEEK_END)
    if file.tell() > MAX_FILE_SIZE:
        return error("文件过大，最大支持 10MB", 400)
    file.seek(0)

    original_name = file.filename
    file_id = generate_uuid()

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

    with get_db() as (conn, cursor):
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

    return success({
        "file_id": file_id,
        "name": original_name,
        "uploaded_at": uploaded_at
    }, code=201)
