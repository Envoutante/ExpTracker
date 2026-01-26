from flask import Flask, send_from_directory
from flask_cors import CORS
from database import db_session, init_db
from routes import api
import os

app = Flask(__name__, static_folder='../frontend/dist')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 注册 API 蓝图
app.register_blueprint(api, url_prefix='/api')

# 初始化数据库
init_db()

# 服务前端静态文件
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    print("=" * 50)
    print("ExpTracker 实验日志管理系统启动中...")
    print("访问地址: http://localhost:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)
