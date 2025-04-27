from flask import Blueprint, request
from database import get_db
from utils.idgen import generate_uuid
from utils.response import success, error

folders_bp = Blueprint("folders", __name__)

@folders_bp.route("/tree", methods=["GET"])
def get_folder_tree():
    """
    Get the hierarchical tree structure of all folders.
    ---
    tags:
      - Folder
    responses:
      200:
        description: Folder tree structure
    """
    with get_db() as (conn, cursor):
        cursor.execute("SELECT * FROM folders")
        folders = cursor.fetchall()

    # Convert to tree structure
    folder_dict = {f["id"]: {"id": f["id"], "name": f["name"], "parent_id": f["parent_id"], "children": []} for f in folders}
    root = []

    for folder in folder_dict.values():
        if folder["parent_id"]:
            parent = folder_dict.get(folder["parent_id"])
            if parent:
                parent["children"].append(folder)
        else:
            root.append(folder)

    return success(root)

@folders_bp.route("", methods=["POST"])
def create_folder():
    """
    Create a new folder (supports parent_id).
    ---
    tags:
      - Folder
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: 2024Show
            parent_id:
              type: string
              nullable: true
              example: null
    responses:
      201:
        description: Creation successful
    """
    data = request.get_json()
    name = data.get("name")
    parent_id = data.get("parent_id")

    if not name:
        return error("The name field is required", 400)

    folder_id = generate_uuid()

    with get_db() as (conn, cursor):
        name_clean = name.strip()

        # Check if parent_id exists
        if parent_id:
            cursor.execute("SELECT id FROM folders WHERE id = ?", (parent_id,))
            if not cursor.fetchone():
                return error("parent_id does not exist", 400)

        # Check for duplicate names at the same level
        if parent_id:
            cursor.execute("SELECT id FROM folders WHERE name = ? AND parent_id = ?", (name_clean, parent_id))
        else:
            cursor.execute("SELECT id FROM folders WHERE name = ? AND parent_id IS NULL", (name_clean,))
        
        if cursor.fetchone():
            return error("A folder with the same name already exists at the same level", 409)

        # Insert the new folder
        cursor.execute("INSERT INTO folders (id, name, parent_id) VALUES (?, ?, ?)", (folder_id, name_clean, parent_id))

    return success({
        "id": folder_id,
        "name": name,
        "parent_id": parent_id
    }, code=201)

def get_all_descendant_folder_ids(folder_id, cursor):
    """Recursively find all descendant folder IDs (including itself)."""
    ids = [folder_id]
    cursor.execute("SELECT id FROM folders WHERE parent_id = ?", (folder_id,))
    children = cursor.fetchall()
    for child in children:
        ids.extend(get_all_descendant_folder_ids(child["id"], cursor))
    return ids

@folders_bp.route("/<folder_id>", methods=["DELETE"])
def delete_folder(folder_id):
    """
    Delete the specified folder (including all its subfolders).
    ---
    tags:
      - Folder
    parameters:
      - name: folder_id
        in: path
        type: string
        required: true
        description: Folder ID
    responses:
      200:
        description: Deletion successful
    """
    with get_db() as (conn, cursor):
        # Check if the folder exists
        cursor.execute("SELECT * FROM folders WHERE id = ?", (folder_id,))
        if not cursor.fetchone():
            return error("Folder not found", 404)

        # Recursively get all descendant folder IDs
        all_ids = get_all_descendant_folder_ids(folder_id, cursor)

        # Clean up associations in file_folders
        for fid in all_ids:
            cursor.execute("DELETE FROM file_folders WHERE folder_id = ?", (fid,))
            cursor.execute("DELETE FROM folders WHERE id = ?", (fid,))

    return success({
        "deleted_folder_ids": all_ids
    }, 200)

@folders_bp.route("/search", methods=["GET"])
def search_folders():
    """
    Search folders (fuzzy match by name, returns full paths).
    ---
    tags:
      - Folder
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Folder search keyword
    responses:
      200:
        description: Matched folders and their full paths
    """
    q = request.args.get("q", "").strip()

    if not q:
        return error("A search keyword must be provided", 400)

    with get_db() as (conn, cursor):
        cursor.execute("SELECT * FROM folders")
        all_folders = cursor.fetchall()
        folder_dict = {f["id"]: dict(f) for f in all_folders}

        def build_full_path(folder_id):
            path = []
            while folder_id and folder_id in folder_dict:
                f = folder_dict[folder_id]
                path.insert(0, f["name"])
                folder_id = f["parent_id"]
            return path

        # Find matching folders
        cursor.execute("SELECT * FROM folders WHERE name LIKE ?", (f"%{q}%",))
        matches = cursor.fetchall()

        result = []
        for folder in matches:
            result.append({
                "id": folder["id"],
                "name": folder["name"],
                "parent_id": folder["parent_id"],
                "full_path": build_full_path(folder["id"])
            })

        return success(result)
