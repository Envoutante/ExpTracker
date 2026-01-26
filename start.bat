@echo off
chcp 65001 >nul
echo ======================================
echo   ExpTracker 启动脚本
echo ======================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 检查并安装后端依赖
echo 检查后端依赖...
cd backend

if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt -q

echo 启动后端服务...
start /B python app.py

cd ..

echo.
echo ======================================
echo   系统启动成功！
echo ======================================
echo   访问地址: http://localhost:5000
echo   关闭此窗口将停止服务
echo ======================================
echo.

pause
