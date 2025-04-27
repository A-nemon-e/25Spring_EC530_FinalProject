# 25Spring_EC530_FinalProject

## Note (April 23)

- Add thumbnail support (in the file display page)

## Note (April 2)

~~The conda environment `530-final` is for the backend.~~  
Frontend note: For tags, there is a category called **title**.  
When displaying files, the title's full name should be used.

The `name` field in the `files` table should not be editable after creation.

GPT-proposed project structure (PostgreSQL version):

```
your-project/
├── backend/                    # Backend part
│   ├── app.py                  # Main entry point
│   ├── config.py               # Database configuration
│   ├── models/                 # All SQLAlchemy models
│   │   └── tag.py              # Example model
│   ├── routes/                 # All API route modules
│   │   └── tags.py             # Example route
│   ├── services/               # Business logic modules (optional)
│   ├── database.py             # Database initialization
│   ├── migrations/             # Alembic migrations (if used)
│   └── tests/                  # Unit test code
│       └── test_tags.py
├── frontend/                   # Vue + Element UI project
│   ├── public/                 # Static resources
│   ├── src/                    # Main source code
│   │   ├── components/         # Components (e.g., file tree, tag selector)
│   │   ├── pages/              # Pages
│   │   └── api/                # Axios API wrappers
│   └── vite.config.js          # Build configuration
├── requirements.txt            # Python dependencies
├── package.json                # Frontend dependencies
├── .env                        # Local environment variables (e.g., database connection)
├── README.md                   # Project documentation
└── .gitignore
```

GPT-proposed project structure (SQLite version):

```
├── backend/                        # Root directory for backend code
│   ├── app.py                      # Flask app main entry point, mounting all blueprints
│   ├── database.py                 # SQLite connection wrapper (with foreign key support)
│   ├── init_db.py                  # Create database and 6 table structures (already completed)
│   ├── mydatabase.db               # SQLite database file (auto-generated)
│
│   ├── routes/                     # API modules (split by function)
│   │   ├── tags.py                 # Tags module (create, retrieve tags)
│   │   ├── files.py                # File upload and query
│   │   ├── folders.py              # Folder creation, retrieval, tree structure
│   │   └── search.py               # Search: find files by tag name or alias
│
│   ├── utils/                      # Utility modules (UUID, path handling, validation, etc.)
│   │   ├── idgen.py                # Generate UUID strings
│   │   ├── response.py             # Standardized JSON responses
│   │   └── validation.py           # Parameter validation functions (optional)
│
│   └── config.py                   # Project configuration (database path, upload folder, etc.)
├── uploads/                        # Directory for storing uploaded files
│   └── ...                         # Customizable file system structure
└── README.md                       # Project documentation
```

### API Endpoints

#### Files
| Type | Path | Method | Description |
|:---|:---|:---|:---|
| Upload file | `/api/files/upload` | POST | Upload a file, optionally specify associated folders and tags |
| File details | `/api/files/<file_id>` | GET | Retrieve a single file's information |
| Delete file | `/api/files/<file_id>` | DELETE | Delete a file and its associations |
| Update file info | `/api/files/{file_id}` | PUT | Modify a file's associated tags and folders (explicitly provide empty lists to clear) |
| Search files | `/api/files` | GET | Paginated file retrieval (supports filtering by tag IDs and folder IDs, returns full folder paths and tags) |

#### Folders
| Type | Path | Method | Description |
|:---|:---|:---|:---|
| Get folder tree | `/api/folders/tree` | GET | Retrieve all folder hierarchy structure |
| Create folder | `/api/folders` | POST | Create a new folder (supports parent_id) |
| Delete folder | `/api/folders/<folder_id>` | DELETE | Delete a specified folder |
| Search folders | `/api/folders/search?q=` | GET | Search folders and return full paths |

#### Tags
| Type | Path | Method | Description |
|:---|:---|:---|:---|
| Get tags | `/api/tags` | GET | Retrieve all tags (optionally filter by category) |
| Add tag | `/api/tags` | POST | Create a new tag |
| Add alias | `/api/tags/<tag_id>/alias` | POST | Add an alias to a specific tag |

---

### Database Table Designs

```
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
```

---

### Unified JSON Response Format

| Field | Type | Description |
|:---|:---|:---|
| status | string | "success" or "error" |
| data | dict/null | Result data if successful |
| error | string/null | Error message if failed |
| code | int | HTTP status code (used by frontend logic) |

Successful response example:

```json
{
  "status": "success",
  "code": 201,
  "data": {
    "file_id": "abc123",
    "name": "Score.pdf",
    "uploaded_at": "2025-03-28T20:12:35Z"
  },
  "error": null
}
```

Error response example:

```json
{
  "status": "error",
  "code": 400,
  "data": null,
  "error": "Missing file"
}
```
