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
backend/
├── models/
│   └── tag.py           # 放置 Tag 类
├── database.py          # 初始化 SQLite 引擎和 session
├── app.py               # 启动 Flask 服务
└── mydatabase.db        # SQLite 数据库文件（自动生成）

```