import sqlite3

# 连接 SQLite 数据库（会自动创建 mydatabase.db）
conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()

'''
*files*
    id

    name

    upload_path

    size

    uploaded_at

*folders*
    id

    name

    parent_id (支持嵌套)

    created_at

*file_folders*（中间表）
    file_id

    folder_id

*tags*
    id

    name

    category

*tag_aliases*
    tag_id

    alias

*file_tags*
    file_id

    tag_id
'''

# 创建 files 表
cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    upload_path TEXT NOT NULL,
    size BIGINT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 创建 folders 表
cursor.execute("""
CREATE TABLE IF NOT EXISTS folders (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES folders(id)
);
""")

# 创建 file_folders 表
cursor.execute("""
CREATE TABLE IF NOT EXISTS file_folders (
    file_id TEXT,
    folder_id TEXT,
    PRIMARY KEY (file_id, folder_id),
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (folder_id) REFERENCES folders(id)
);
""")

# 创建 tags 表
cursor.execute("""
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL
);
""")

# 创建 tag_aliases 表
cursor.execute("""
CREATE TABLE IF NOT EXISTS tag_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER NOT NULL,
    alias TEXT NOT NULL,
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
""")

# 创建 file_tags 表
cursor.execute("""
CREATE TABLE IF NOT EXISTS file_tags (
    file_id TEXT,
    tag_id INTEGER,
    PRIMARY KEY (file_id, tag_id),
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
""")

# 提交并关闭
conn.commit()
conn.close()
print("✅ 所有表已创建完毕（mydatabase.db）")
