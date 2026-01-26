# 🧪 ExpTracker - 实验日志管理系统

一个专为 PyMARL 强化学习实验设计的本地日志管理系统，帮助你记录实验细节、管理 TensorBoard 日志，让实验管理井井有条。

**ExpTracker** = Experiment Tracker

## ✨ 功能特性

- 📝 **实验记录管理** - 记录实验名称、配置、思路、结果
- 🏷️ **标签分类** - 使用标签组织和检索实验
- 📊 **TensorBoard 集成** - 一键启动 TensorBoard 查看训练曲线
- 🔍 **搜索过滤** - 按名称、状态、标签快速查找实验
- 💾 **本地存储** - 使用 SQLite 本地数据库，无需服务器
- 🚀 **一键启动** - 简单的启动脚本，开箱即用

## 🛠️ 技术栈

- **前端**: Vue 3 + Element Plus + Vite
- **后端**: Flask + SQLAlchemy
- **数据库**: SQLite
- **部署**: 本地一键启动

## 📦 安装依赖

### 后端依赖

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 前端依赖（开发模式）

```bash
cd frontend
npm install
```

## 🚀 快速启动

### 方式一：一键启动（推荐）

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

启动后访问: http://localhost:5000

### 方式二：开发模式

**后端:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

**前端:**
```bash
cd frontend
npm run dev
```

前端开发服务器: http://localhost:3000

## 📖 使用指南

### 1. 创建实验

点击"新建实验"按钮，填写：
- 实验名称（必填）
- 算法和环境
- 实验配置参数（JSON 格式）
- 实验目的和思路
- TensorBoard 日志路径

### 2. 记录实验过程

在实验详情页面记录：
- 观察记录：实验过程中的发现
- 结果数据：关键指标和数值
- 结论：实验总结和下一步计划

### 3. 查看 TensorBoard

在实验列表或详情页点击"启动 TensorBoard"按钮，系统会：
1. 自动启动 TensorBoard 服务
2. 在浏览器中打开 TensorBoard 界面
3. 显示训练曲线和指标

### 4. 搜索和过滤

- 使用搜索框按名称查找实验
- 使用状态筛选器过滤实验
- 使用标签组织相关实验

## 📁 项目结构

```
exptracker/
├── backend/              # 后端代码
│   ├── app.py           # Flask 主应用
│   ├── models.py        # 数据库模型
│   ├── routes.py        # API 路由
│   ├── database.py      # 数据库配置
│   └── requirements.txt # Python 依赖
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── views/      # 页面组件
│   │   ├── api/        # API 调用
│   │   ├── App.vue     # 根组件
│   │   └── main.js     # 入口文件
│   └── package.json    # Node 依赖
├── start.sh            # Linux/Mac 启动脚本
├── start.bat           # Windows 启动脚本
└── README.md           # 项目文档
```

## 🔧 配置说明

### TensorBoard 端口

默认端口为 6006，可在实验详情页修改。如果端口被占用，系统会提示错误。

### 数据库位置

SQLite 数据库文件位于 `backend/experiments.db`，建议定期备份。

## 💡 使用技巧

1. **标签使用**: 为实验添加有意义的标签，如 "baseline"、"ablation"、"best"
2. **配置参数**: 使用 JSON 格式记录完整的超参数配置
3. **实验命名**: 使用清晰的命名规则，如 "QMIX-3m-lr0.001-20240122"
4. **定期备份**: 定期备份 experiments.db 文件

## 🐛 常见问题

**Q: TensorBoard 启动失败？**
A: 检查日志路径是否正确，确保已安装 tensorboard (`pip install tensorboard`)

**Q: 端口被占用？**
A: 修改 backend/app.py 中的端口号，或关闭占用端口的程序

**Q: 前端无法连接后端？**
A: 确保后端服务正在运行，检查防火墙设置

## 📝 待办事项

- [ ] 实验对比功能
- [ ] 数据导出（CSV/JSON）
- [ ] 图表可视化
- [ ] 实验模板
- [ ] 暗色主题

## 📄 许可证

MIT License

---

**祝你实验顺利！🎉**
