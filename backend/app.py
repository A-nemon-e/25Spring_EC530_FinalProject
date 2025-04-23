from flask import Flask
from flask_cors import CORS



from flasgger import Swagger

from routes.tags import tags_bp
from routes.files import files_bp
from routes.folders import folders_bp
# 可继续添加更多 blueprint：folders_bp, search_bp 等

app = Flask(__name__)
swagger = Swagger(app)
CORS(app)
# 注册蓝图
app.register_blueprint(tags_bp, url_prefix="/api/tags")
app.register_blueprint(files_bp, url_prefix="/api/files")
app.register_blueprint(folders_bp, url_prefix="/api/folders")

# 启动服务器
if __name__ == "__main__":
    app.run(debug=True)
