from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from routes.tags import tags_bp
from routes.files import files_bp
from routes.folders import folders_bp
# Additional blueprints can be added here: folders_bp, search_bp, etc.

app = Flask(__name__)
swagger = Swagger(app)
CORS(app)

# Register blueprints
app.register_blueprint(tags_bp, url_prefix="/api/tags")
app.register_blueprint(files_bp, url_prefix="/api/files")
app.register_blueprint(folders_bp, url_prefix="/api/folders")

# Start the server
if __name__ == "__main__":
    app.run(debug=True)

