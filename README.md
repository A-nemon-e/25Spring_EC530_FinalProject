# 25Spring_EC530_FinalProject

## Note April 2
conda env 530-final is for backend.
给前端的note: tag有一个category是title。文件展示需要用这个title的name（全称）

表files里的name创建时应不能修改

GPT proposed project structure:(PostgreSQL)

```
your-project/
├── backend/                    # 后端部分
│   ├── app.py                  # 主入口
│   ├── config.py               # 数据库配置
│   ├── models/                 # 所有 SQLAlchemy 模型
│   │   └── tag.py              # 示例模型
│   ├── routes/                 # 所有 API 路由模块
│   │   └── tags.py             # 示例路由
│   ├── services/               # 逻辑函数模块（可选）
│   ├── database.py             # 数据库初始化
│   ├── migrations/             # Alembic 数据库迁移（如使用）
│   └── tests/                  # 单元测试代码
│       └── test_tags.py
├── frontend/                   # Vue + Element UI 项目
│   ├── public/                 # 静态资源
│   ├── src/                    # 主代码目录
│   │   ├── components/         # 组件（如文件树、标签选择器）
│   │   ├── pages/              # 页面
│   │   └── api/                # axios 接口封装
│   └── vite.config.js          # 构建配置
├── requirements.txt            # Python 依赖
├── package.json                # 前端依赖
├── .env                        # 本地环境变量（数据库连接等）
├── README.md                   # 项目文档
└── .gitignore

```

GPT proposed project structure:(SQLite)
```
├── backend/                        # 后端代码根目录
│   ├── app.py                      # Flask 应用主入口，挂载所有蓝图
│   ├── database.py                 # SQLite 连接封装（含外键开启）
│   ├── init_db.py                  # 创建数据库和 6 张表结构（你已完成）
│   ├── mydatabase.db               # SQLite 数据文件（自动生成）
│
│   ├── routes/                     # 路由功能模块（按功能拆分）
│   │   ├── tags.py                 # 标签模块（创建、获取标签）
│   │   ├── files.py                # 文件上传、查询
│   │   ├── folders.py              # 文件夹创建/获取/树形结构
│   │   └── search.py               # 搜索：通过标签名或别名找文件
│
│   ├── utils/                      # 工具类（UUID、路径、校验等）
│   │   ├── idgen.py                # 生成 UUID 字符串
│   │   ├── response.py             # 统一Json回复格式
│   │   └── validation.py           # 参数验证函数（可选）
│
│   └── config.py                   # 项目配置（数据库路径、上传目录等）
├── uploads/                        # 上传文件的存储目录
│   └── ...                         # 文件系统结构自定义
└── README.md                       # 项目说明

```
### 路由
```
功能类型	路径	方法	描述
上传文件	/api/files/upload	POST	上传文件并指定所属文件夹和标签
文件列表	/api/files	GET	分页获取所有文件
文件详情	/api/files/<file_id>	GET	获取单个文件信息
删除文件	/api/files/<file_id>	DELETE	删除文件及关联

功能类型	路径	方法	描述
获取文件夹	/api/folders/tree	GET	获取所有文件夹层级结构
创建文件夹	/api/folders	POST	新建文件夹（支持 parent_id）
删除文件夹	/api/folders/<folder_id>	DELETE	删除指定文件夹

功能类型	路径	方法	描述
获取标签	/api/tags	GET	获取所有标签（可按分类筛选）
添加标签	/api/tags	POST	新建标签
添加别名	/api/tags/<tag_id>/alias	POST	给指定标签添加一个别名

功能类型	路径	方法	描述
搜索文件	/api/search?q=xxx	GET	输入 tag 名或 alias，查文件
多条件搜索	/api/search?q=xxx&folder=...&tag=...	GET	组合搜索

```


### 表：表设计

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
```

### 表：统一返回Json格式

字段	类型	描述
status	string	"success" or "error"
data	dict/null	成功时返回的结果数据
error	string/null	错误时的消息文字
code	int	HTTP 状态码（用于前端逻辑处理）

成功返回：

```
{
  "status": "success",
  "code": 201,
  "data": {
    "file_id": "abc123",
    "name": "谱子.pdf",
    "uploaded_at": "2025-03-28T20:12:35Z"
  },
  "error": null
}
```
错误返回：

```
{
  "status": "error",
  "code": 400,
  "data": null,
  "error": "缺少文件"
}

```
