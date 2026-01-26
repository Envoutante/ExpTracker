#!/bin/bash

# ========== 配置区域 ==========
CONDA_ENV_NAME="py312"
# ==============================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 启动后端的命令（conda + venv）
BACKEND_CMD="
cd '$SCRIPT_DIR'
echo '======================================'
echo '  ExpTracker 后端服务'
echo '======================================'

# 初始化 conda
if [ -f \"\$HOME/miniconda3/etc/profile.d/conda.sh\" ]; then
    source \"\$HOME/miniconda3/etc/profile.d/conda.sh\"
elif [ -f \"\$HOME/anaconda3/etc/profile.d/conda.sh\" ]; then
    source \"\$HOME/anaconda3/etc/profile.d/conda.sh\"
elif [ -f \"\$HOME/miniforge3/etc/profile.d/conda.sh\" ]; then
    source \"\$HOME/miniforge3/etc/profile.d/conda.sh\"
elif [ -f \"/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh\" ]; then
    source \"/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh\"
fi
conda activate $CONDA_ENV_NAME
echo \"Conda 环境已激活: $CONDA_ENV_NAME\"

cd backend
if [ ! -d \"venv\" ]; then
    echo \"创建虚拟环境...\"
    python3 -m venv venv
fi
source venv/bin/activate
echo \"Venv 环境已激活\"

pip install -r requirements.txt -q
echo ''
echo '后端服务启动中... http://localhost:5000'
echo '按 Ctrl+C 停止服务'
echo ''
python3 app.py
"

# 启动前端的命令（conda）
FRONTEND_CMD="
cd '$SCRIPT_DIR'
echo '======================================'
echo '  ExpTracker 前端服务'
echo '======================================'

# 初始化 conda
if [ -f \"\$HOME/miniconda3/etc/profile.d/conda.sh\" ]; then
    source \"\$HOME/miniconda3/etc/profile.d/conda.sh\"
elif [ -f \"\$HOME/anaconda3/etc/profile.d/conda.sh\" ]; then
    source \"\$HOME/anaconda3/etc/profile.d/conda.sh\"
elif [ -f \"\$HOME/miniforge3/etc/profile.d/conda.sh\" ]; then
    source \"\$HOME/miniforge3/etc/profile.d/conda.sh\"
elif [ -f \"/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh\" ]; then
    source \"/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh\"
fi
conda activate $CONDA_ENV_NAME
echo \"Conda 环境已激活: $CONDA_ENV_NAME\"

cd frontend
if [ ! -d \"node_modules\" ]; then
    echo \"安装前端依赖...\"
    npm install
fi
echo ''
echo '前端服务启动中... http://localhost:5173'
echo '按 Ctrl+C 停止服务'
echo ''
npm run dev
"

echo "======================================"
echo "  ExpTracker 启动脚本"
echo "======================================"

echo "启动后端服务（新终端窗口）..."
osascript -e "tell application \"Terminal\" to do script \"$BACKEND_CMD\""

sleep 1

echo "启动前端服务（新终端窗口）..."
osascript -e "tell application \"Terminal\" to do script \"$FRONTEND_CMD\""

echo ""
echo "======================================"
echo "  服务已在独立窗口中启动！"
echo "======================================"
echo "  后端地址: http://localhost:5000"
echo "  前端地址: http://localhost:5173"
echo "  请在各自的终端窗口中按 Ctrl+C 停止服务"
echo "======================================"
