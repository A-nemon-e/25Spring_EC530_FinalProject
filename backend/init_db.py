import sqlite3

# Connect to the SQLite database (will automatically create mydatabase.db if it doesn't exist)
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
    parent_id (supports nesting)
    created_at

*file_folders* (association table)
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

# Create the files table
cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    upload_path TEXT NOT NULL,
    size BIGINT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Create the folders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS folders (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES folders(id)
);
""")

# Create the file_folders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS file_folders (
    file_id TEXT,
    folder_id TEXT,
    PRIMARY KEY (file_id, folder_id),
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (folder_id) REFERENCES folders(id)
);
""")

# Create the tags table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL
);
""")

# Create the tag_aliases table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tag_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER NOT NULL,
    alias TEXT NOT NULL,
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
""")

# Create the file_tags table
cursor.execute("""
CREATE TABLE IF NOT EXISTS file_tags (
    file_id TEXT,
    tag_id INTEGER,
    PRIMARY KEY (file_id, tag_id),
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
""")

# Commit the changes and close the connection
conn.commit()
conn.close()
print("✅ All tables have been successfully created (mydatabase.db)")
