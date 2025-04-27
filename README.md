# 25Spring_EC530_FinalProject

## Note (April 23)

- Add thumbnail support (in the file display page)

## Note (April 2)

~~The conda environment `530-final` is for the backend.~~  
Frontend note: For tags, there is a category called **title**.  
When displaying files, you should use the **full name** of the title.

The `name` field in the `files` table should **not be editable** after creation.

GPT-proposed project structure (PostgreSQL version):

```
your-project/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models/
│   │   └── tag.py
│   ├── routes/
│   │   └── tags.py
│   ├── services/
│   ├── database.py
│   ├── migrations/
│   └── tests/
│       └── test_tags.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   └── vite.config.js
├── requirements.txt
├── package.json
├── .env
├── README.md
└── .gitignore
```

GPT-proposed project structure (SQLite version):

```
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── init_db.py
│   ├── mydatabase.db
│   ├── routes/
│   │   ├── tags.py
│   │   ├── files.py
│   │   ├── folders.py
│   │   └── search.py
│   ├── utils/
│   │   ├── idgen.py
│   │   ├── response.py
│   │   └── validation.py
│   └── config.py
├── uploads/
│   └── ...
└── README.md
```

### API Endpoints

#### Files
| Function | Path | Method | Description |
|:---|:---|:---|:---|
| Upload file | `/api/files/upload` | POST | Upload a file and optionally specify associated folders and tags |
| Get file details | `/api/files/<file_id>` | GET | Retrieve information about a single file |
| Delete file | `/api/files/<file_id>` | DELETE | Delete a file and its associations |
| Update file metadata | `/api/files/{file_id}` | PUT | Update file's associated tags and folders (empty lists will clear) |
| Search files | `/api/files` | GET | Paginated retrieval of files (filter by tag IDs and folder IDs, return full folder path and tags) |

#### Folders
| Function | Path | Method | Description |
|:---|:---|:---|:---|
| Get folder tree | `/api/folders/tree` | GET | Retrieve all folders in a hierarchical structure |
| Create folder | `/api/folders` | POST | Create a new folder (supports `parent_id`) |
| Delete folder | `/api/folders/<folder_id>` | DELETE | Delete a specific folder |
| Search folders | `/api/folders/search?q=` | GET | Search folders by keyword and return full path |

#### Tags
| Function | Path | Method | Description |
|:---|:---|:---|:---|
| Get tags | `/api/tags` | GET | Retrieve all tags (optional category filter) |
| Add tag | `/api/tags` | POST | Create a new tag |
| Add alias | `/api/tags/<tag_id>/alias` | POST | Add an alias to a specific tag |

---

### Database Schema

```
* files *
    id
    name
    upload_path
    size
    uploaded_at

* folders *
    id
    name
    parent_id (supports nesting)
    created_at

* file_folders * (association table)
    file_id
    folder_id

* tags *
    id
    name
    category

* tag_aliases *
    tag_id
    alias

* file_tags *
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
| code | int | HTTP status code (for frontend logic handling) |

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
