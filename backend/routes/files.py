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
    Upload a file and assign tags and folders.
    ---
    tags:
      - File
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: The PDF file to upload
      - name: tags
        in: formData
        type: string
        required: false  # ✅ Changed to false
        description: JSON string of tag_id list (optional)
      - name: folders
        in: formData
        type: string
        required: false  # ✅ Changed to false
        description: JSON string of folder_id list (optional)
    responses:
      201:
        description: Upload successful
    """
    file = request.files.get("file")
    tags_raw = request.form.get("tags")
    folders_raw = request.form.get("folders")

    if not file:
        return error("Missing file", 400)

    tag_ids = []
    folder_ids = []

    try:
        if tags_raw:
            tag_ids = json.loads(tags_raw)
        if folders_raw:
            folder_ids = json.loads(folders_raw)
    except Exception:
        return error("tags and folders must be JSON array strings", 400)

    if not isinstance(tag_ids, list) or not isinstance(folder_ids, list):
        return error("tags and folders must be arrays", 400)

    original_name = file.filename
    file_id = generate_uuid()

    # Generate file path
    today = datetime.now(timezone.utc)
    folder_name = today.strftime("%Y_%m")
    folder_path = os.path.join(UPLOAD_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    filename = f"{file_id}.pdf"
    save_path = os.path.join(folder_path, secure_filename(filename))

    try:
        file.save(save_path)
    except Exception as e:
        return error(f"Failed to save file: {str(e)}", 500)

    uploaded_at = today.isoformat()

    try:
        with get_db() as (conn, cursor):
            # Insert into files table
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

            # Insert into file_tags
            for tag_id in tag_ids:
                cursor.execute("SELECT id FROM tags WHERE id = ?", (tag_id,))
                if not cursor.fetchone():
                    raise ValueError(f"Tag ID not found: {tag_id}")
                cursor.execute("INSERT INTO file_tags (file_id, tag_id) VALUES (?, ?)", (file_id, tag_id))

            # Insert into file_folders
            for folder_id in folder_ids:
                cursor.execute("SELECT id FROM folders WHERE id = ?", (folder_id,))
                if not cursor.fetchone():
                    raise ValueError(f"Folder ID not found: {folder_id}")
                cursor.execute("INSERT INTO file_folders (file_id, folder_id) VALUES (?, ?)", (file_id, folder_id))

    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        return error(f"Database write failed: {str(e)}", 500)

    return success({
        "file_id": file_id,
        "name": original_name,
        "uploaded_at": uploaded_at
    }, code=201)

@files_bp.route("/<file_id>", methods=["GET"])
def get_file(file_id):
    """
    Get details of a single file.
    ---
    tags:
      - File
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: File ID
    responses:
      200:
        description: Successfully returned file details
    """
    with get_db() as (conn, cursor):
        # Query file main information
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        file = cursor.fetchone()
        if not file:
            return error("File not found", 404)

        # Query tag information
        cursor.execute("""
            SELECT t.id, t.name, t.category
            FROM file_tags ft
            JOIN tags t ON ft.tag_id = t.id
            WHERE ft.file_id = ?
        """, (file_id,))
        tags = [dict(row) for row in cursor.fetchall()]

        # Query folder information
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
    Update file's tags and folder bindings (empty list means clear, must explicitly provide both fields)
    ---
    tags:
      - File
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
        description: Update successful
    """
    data = request.get_json()
    tags = data.get("tags")
    folders = data.get("folders")

    if tags is None or folders is None:
        return error("Both tags and folders must be provided (can be empty arrays)", 400)

    if not isinstance(tags, list) or not isinstance(folders, list):
        return error("tags and folders must be arrays", 400)

    with get_db() as (conn, cursor):
        # Check if file exists
        cursor.execute("SELECT id FROM files WHERE id = ?", (file_id,))
        if not cursor.fetchone():
            return error("File not found", 404)

        # Clear old bindings
        cursor.execute("DELETE FROM file_tags WHERE file_id = ?", (file_id,))
        cursor.execute("DELETE FROM file_folders WHERE file_id = ?", (file_id,))

        # Insert new tags
        for tag_id in tags:
            cursor.execute("SELECT id FROM tags WHERE id = ?", (tag_id,))
            if not cursor.fetchone():
                return error(f"Tag not found: {tag_id}", 400)
            cursor.execute("INSERT INTO file_tags (file_id, tag_id) VALUES (?, ?)", (file_id, tag_id))

        # Insert new folders
        for folder_id in folders:
            cursor.execute("SELECT id FROM folders WHERE id = ?", (folder_id,))
            if not cursor.fetchone():
                return error(f"Folder not found: {folder_id}", 400)
            cursor.execute("INSERT INTO file_folders (file_id, folder_id) VALUES (?, ?)", (file_id, folder_id))

    return success({"file_id": file_id}, 200)

@files_bp.route("", methods=["GET"])
def list_files():
    """
    Get a paginated list of files (supporting multiple tag ID and folder ID intersection, returns full path).
    ---
    tags:
      - File
    parameters:
      - name: tag_ids
        in: query
        type: string
        required: false
        description: Multiple tag_ids separated by commas (intersection filter, e.g., tag1,tag2 means both must be present)
      - name: folder_ids
        in: query
        type: string
        required: false
        description: Multiple folder IDs separated by commas (intersection filter)
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number, starting from 1
      - name: size
        in: query
        type: integer
        required: false
        default: 20
        description: Number of items per page
    responses:
      200:
        description: Successfully returned paginated file list
    """
    folder_ids_str = request.args.get("folder_ids")
    folder_ids = folder_ids_str.split(",") if folder_ids_str else []

    tag_ids_str = request.args.get("tag_ids")
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 2000000))
    offset = (page - 1) * size

    tag_ids = tag_ids_str.split(",") if tag_ids_str else []

    if not folder_ids and not tag_ids:
        return error("Must provide at least one of tag_ids or folder_ids", 400)

    with get_db() as (conn, cursor):
        # 1. Tag_ids subquery
        file_ids = None
        if tag_ids:
            tag_placeholders = ','.join(['?'] * len(tag_ids))
            tag_sql = f"""
                SELECT file_id FROM file_tags
                WHERE tag_id IN ({tag_placeholders})
                GROUP BY file_id
                HAVING COUNT(DISTINCT tag_id) = ?
            """
            cursor.execute(tag_sql, tag_ids + [len(tag_ids)])
            file_ids = [row["file_id"] for row in cursor.fetchall()]
            if not file_ids:
                return success({"total": 0, "files": []})

        # 2. Build main query
        where_clauses = []
        params = []

        if file_ids is not None:
            placeholders = ','.join(['?'] * len(file_ids))
            where_clauses.append(f"f.id IN ({placeholders})")
            params.extend(file_ids)

        if folder_ids:
            for fid in folder_ids:
                where_clauses.append("""
                    EXISTS (
                        SELECT 1 FROM file_folders ff
                        WHERE ff.file_id = f.id AND ff.folder_id = ?
                    )
                """)
                params.append(fid)

        where_sql = "WHERE " + " AND ".join(where_clauses)

        # 3. Query file records
        cursor.execute(f"""
            SELECT * FROM files f
            {where_sql}
            ORDER BY f.uploaded_at DESC
            LIMIT ? OFFSET ?
        """, params + [size, offset])
        files = cursor.fetchall()

        # 4. Query total count
        cursor.execute(f"""
            SELECT COUNT(*) FROM files f
            {where_sql}
        """, params)
        total = cursor.fetchone()[0]

        # 5. Load all folders to build full path
        cursor.execute("SELECT id, name, parent_id FROM folders")
        folder_dict = {f["id"]: dict(f) for f in cursor.fetchall()}

        def build_full_path(folder_id):
            path = []
            while folder_id and folder_id in folder_dict:
                folder = folder_dict[folder_id]
                path.insert(0, folder["name"])
                folder_id = folder["parent_id"]
            return path

        result = []
        for f in files:
            file_id = f["id"]

            # Query tags
            cursor.execute("""
                SELECT t.id, t.name, t.category
                FROM file_tags ft JOIN tags t ON ft.tag_id = t.id
                WHERE ft.file_id = ?
            """, (file_id,))
            tags = [dict(row) for row in cursor.fetchall()]

            # Query folders and build full paths
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
    Delete a file and all its associations.
    ---
    tags:
      - File
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: File ID to delete
    responses:
      200:
        description: Delete successful
    """
    with get_db() as (conn, cursor):
        # 1. Check if file exists
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        file = cursor.fetchone()
        if not file:
            return error("File not found", 404)

        upload_path = file["upload_path"]

        # 2. Delete local file
        if upload_path and os.path.exists(upload_path):
            try:
                os.remove(upload_path)
            except Exception as e:
                return error(f"Failed to delete local file: {str(e)}", 500)

        # 3. Delete all bindings from intermediate tables
        cursor.execute("DELETE FROM file_tags WHERE file_id = ?", (file_id,))
        cursor.execute("DELETE FROM file_folders WHERE file_id = ?", (file_id,))

        # 4. Delete main file record
        cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))

    return success({"deleted_file_id": file_id}, 200)
