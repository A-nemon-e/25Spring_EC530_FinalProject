from flask import Flask
from flasgger import Swagger

from routes.tags import tags_bp
from routes.files import files_bp
# 可继续添加更多 blueprint：folders_bp, search_bp 等

app = Flask(__name__)
swagger = Swagger(app)

# 注册蓝图
app.register_blueprint(tags_bp, url_prefix="/api/tags")
app.register_blueprint(files_bp, url_prefix="/api/files")

# 启动服务器
if __name__ == "__main__":
    app.run(debug=True)
