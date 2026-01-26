# 使用说明

## 启动系统

### 首次使用

1. 安装依赖（只需一次）：
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install tensorboard  # 用于查看训练曲线
```

2. 启动系统：
```bash
./start.sh  # Linux/Mac
# 或
start.bat   # Windows
```

3. 打开浏览器访问: http://localhost:5000

### 日常使用

直接运行启动脚本即可：
```bash
./start.sh  # Linux/Mac
```

## 功能使用

### 1. 创建实验

1. 点击右上角"新建实验"按钮
2. 填写基本信息：
   - **实验名称**（必填）：如 "QMIX-3m-baseline"
   - **状态**：运行中/已完成/失败
   - **标签**：可以输入多个标签，如 "baseline", "3m", "qmix"
   - **描述**：简短描述实验内容

3. 填写实验配置：
   - **算法**：如 QMIX, VDN, MAPPO
   - **环境**：如 3m, 8m, corridor
   - **配置参数**：JSON 格式，例如：
   ```json
   {
     "lr": 0.0005,
     "batch_size": 32,
     "epsilon_start": 1.0,
     "epsilon_finish": 0.05,
     "epsilon_anneal_time": 50000
   }
   ```

4. 填写实验思路：
   - **实验目的**：说明为什么做这个实验，想验证什么假设

5. 配置 TensorBoard：
   - **日志路径**：TensorBoard 日志文件的完整路径
   - **端口**：默认 6006，如果冲突可以修改

6. 点击"保存"

### 2. 查看实验列表

主页显示所有实验，包含：
- ID、名称、算法、环境、状态、创建时间
- 可以按名称搜索
- 可以按状态筛选
- 支持分页浏览

### 3. 编辑实验

1. 在实验列表点击"编辑"按钮
2. 修改任何字段
3. 在实验过程中可以随时更新：
   - **观察记录**：记录训练过程中的发现
   - **结果数据**：记录关键指标，如最终胜率、平均奖励等
   - **结论**：实验结束后的总结和下一步计划

### 4. 启动 TensorBoard

**方式一：从列表启动**
- 在实验列表点击"TensorBoard"按钮
- 系统会自动启动 TensorBoard 并打开浏览器

**方式二：从详情页启动**
- 进入实验详情页
- 在 TensorBoard 区域点击"启动 TensorBoard"
- 可以查看运行状态
- 可以点击"停止 TensorBoard"关闭服务

### 5. 删除实验

- 在实验列表点击"删除"按钮
- 确认后删除（不可恢复）

## 最佳实践

### 实验命名规范

建议使用清晰的命名规则，例如：
- `算法-环境-特征-日期`
- 示例：`QMIX-3m-baseline-20240122`
- 示例：`VDN-8m-lr0001-20240122`

### 标签使用建议

使用标签组织实验：
- **算法标签**：qmix, vdn, mappo
- **环境标签**：3m, 8m, corridor
- **类型标签**：baseline, ablation, tuning
- **状态标签**：best, failed, promising

### 配置参数记录

使用 JSON 格式记录完整配置，方便复现：
```json
{
  "algorithm": "qmix",
  "env": "3m",
  "lr": 0.0005,
  "batch_size": 32,
  "buffer_size": 5000,
  "epsilon_start": 1.0,
  "epsilon_finish": 0.05,
  "epsilon_anneal_time": 50000,
  "gamma": 0.99,
  "target_update_interval": 200
}
```

### 实验记录技巧

**实验目的**（开始前填写）：
```
验证 QMIX 在 3m 地图上的基线性能。
预期胜率应该在 90% 以上。
```

**观察记录**（实验过程中更新）：
```
- 前 10k 步：智能体学会基本移动
- 20k 步：开始出现协作行为
- 50k 步：胜率达到 80%
- 100k 步：胜率稳定在 95%
- 发现：epsilon 衰减速度对性能影响很大
```

**结果数据**（实验结束后填写）：
```
最终胜率: 96.5%
平均奖励: 18.3
训练时长: 2.5 小时
最佳模型: step_120000
```

**结论**（实验结束后填写）：
```
QMIX 在 3m 上表现良好，达到预期性能。
下一步：
1. 尝试在 8m 上测试
2. 进行消融实验，测试 mixing network 的影响
3. 对比 VDN 的性能
```

## 工作流程示例

### 典型的实验流程

1. **创建实验记录**
   - 填写实验名称、算法、环境
   - 记录配置参数
   - 说明实验目的

2. **运行 PyMARL 代码**
   - 使用命令行运行训练脚本
   - 确保 TensorBoard 日志正确保存

3. **定期更新记录**
   - 每隔一段时间查看 TensorBoard
   - 在系统中更新观察记录

4. **实验结束**
   - 记录最终结果数据
   - 写下结论和下一步计划
   - 更新实验状态为"已完成"或"失败"

5. **对比分析**
   - 使用搜索和标签功能找到相关实验
   - 对比不同实验的配置和结果
   - 为下一个实验做准备

## 数据管理

### 备份数据

数据库文件位于 `backend/experiments.db`，定期备份：
```bash
cp backend/experiments.db backend/experiments_backup_$(date +%Y%m%d).db
```

### 导出数据

未来版本将支持导出功能，可以导出为 JSON 或 CSV 格式。

## 常见问题

**Q: 如何修改 TensorBoard 端口？**
A: 在实验详情页的 TensorBoard 区域修改端口号。

**Q: 可以同时运行多个 TensorBoard 吗？**
A: 可以，只要使用不同的端口号。

**Q: 实验记录可以导出吗？**
A: 当前版本数据存储在 SQLite 数据库中，可以直接备份数据库文件。

**Q: 如何查看历史实验？**
A: 使用搜索功能或标签筛选，所有实验都会保存在列表中。

**Q: 可以上传实验相关文件吗？**
A: 当前版本不支持文件上传，建议在描述中记录文件路径。

---

祝你实验顺利！如有问题，请查看 README.md 或 INSTALL.md。
