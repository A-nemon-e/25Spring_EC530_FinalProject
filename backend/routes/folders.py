from flask import Blueprint, request
from database import get_db
from utils.idgen import generate_uuid
from utils.response import success, error

folders_bp = Blueprint("folders", __name__)

@folders_bp.route("/tree", methods=["GET"])
def get_folder_tree():
    """
    获取所有文件夹的层级树结构
    ---
    tags:
      - 文件夹
    responses:
      200:
        description: 文件夹树结构
    """
    with get_db() as (conn, cursor):
        cursor.execute("SELECT * FROM folders")
        folders = cursor.fetchall()

    # 转为树结构
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
    创建新文件夹（支持 parent_id）
    ---
    tags:
      - 文件夹
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: 2024演出
            parent_id:
              type: string
              nullable: true
              example: null
    responses:
      201:
        description: 创建成功
    """
    data = request.get_json()
    name = data.get("name")
    parent_id = data.get("parent_id")

    if not name:
        return error("name 是必填字段", 400)

    folder_id = generate_uuid()

    with get_db() as (conn, cursor):
        name_clean = name.strip()

        # 检查 parent_id 是否存在
        if parent_id:
            cursor.execute("SELECT id FROM folders WHERE id = ?", (parent_id,))
            if not cursor.fetchone():
                return error("parent_id 不存在", 400)

        # 检查同级目录是否重名
        if parent_id:
            cursor.execute("SELECT id FROM folders WHERE name = ? AND parent_id = ?", (name_clean, parent_id))
        else:
            cursor.execute("SELECT id FROM folders WHERE name = ? AND parent_id IS NULL", (name_clean,))
        
        if cursor.fetchone():
            return error("同一目录下已存在同名文件夹", 409)

        # 插入
        cursor.execute("INSERT INTO folders (id, name, parent_id) VALUES (?, ?, ?)", (folder_id, name_clean, parent_id))


    return success({
        "id": folder_id,
        "name": name,
        "parent_id": parent_id
    }, code=201)

def get_all_descendant_folder_ids(folder_id, cursor):
    """递归查找所有子目录 ID（含自己）"""
    ids = [folder_id]
    cursor.execute("SELECT id FROM folders WHERE parent_id = ?", (folder_id,))
    children = cursor.fetchall()
    for child in children:
        ids.extend(get_all_descendant_folder_ids(child["id"], cursor))
    return ids

@folders_bp.route("/<folder_id>", methods=["DELETE"])
def delete_folder(folder_id):
    """
    删除指定文件夹（含所有子文件夹）
    ---
    tags:
      - 文件夹
    parameters:
      - name: folder_id
        in: path
        type: string
        required: true
        description: 文件夹 ID
    responses:
      200:
        description: 删除成功
    """
    with get_db() as (conn, cursor):
        # 检查是否存在
        cursor.execute("SELECT * FROM folders WHERE id = ?", (folder_id,))
        if not cursor.fetchone():
            return error("文件夹不存在", 404)

        # 递归获取所有子文件夹 ID
        all_ids = get_all_descendant_folder_ids(folder_id, cursor)

        # 清理 file_folders 中的关联
        for fid in all_ids:
            cursor.execute("DELETE FROM file_folders WHERE folder_id = ?", (fid,))
            cursor.execute("DELETE FROM folders WHERE id = ?", (fid,))

    return success({
        "deleted_folder_ids": all_ids
    }, 200)
