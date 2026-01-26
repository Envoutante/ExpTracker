# 安装指南

## 快速开始（3 步）

### 1. 安装后端依赖

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 构建前端（可选，用于生产环境）

如果你想要生产环境部署，需要构建前端：

```bash
cd frontend
npm install
npm run build
```

构建后的文件会在 `frontend/dist` 目录，Flask 会自动服务这些静态文件。

**注意**: 如果只是开发测试，可以跳过这一步，直接使用启动脚本。

### 3. 启动系统

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

访问 http://localhost:5000 即可使用！

## 开发模式

如果你想修改代码并实时预览：

**终端 1 - 后端:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**终端 2 - 前端:**
```bash
cd frontend
npm install  # 首次需要
npm run dev
```

前端开发服务器: http://localhost:3000

## 依赖说明

### 系统要求
- Python 3.7+
- Node.js 16+ (仅开发模式需要)

## 故障排除

### 问题 1: 端口被占用
修改 `backend/app.py` 中的端口号：
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # 改为 5001
```

### 问题 2: 虚拟环境激活失败
确保在正确的目录下执行命令，或手动激活：
```bash
source backend/venv/bin/activate  # Linux/Mac
backend\venv\Scripts\activate.bat  # Windows
```

### 问题 3: 前端构建失败
确保 Node.js 版本 >= 16：
```bash
node --version
```

如果版本过低，请升级 Node.js。
