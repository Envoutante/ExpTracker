from flask import Blueprint, request, jsonify
from models import Experiment, ExperimentGroup
from database import db_session
from config import load_config, save_config, get_events_cache_dir
import subprocess
import webbrowser
import time
import os
import signal
import json
import logging
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

api = Blueprint('api', __name__)

# 存储 TensorBoard 进程和临时目录
tb_processes = {}

# ==================== 导入任务管理 ====================
import uuid

# 存储导入任务状态
import_tasks = {}
import_tasks_lock = threading.Lock()

def create_import_task():
    """创建新的导入任务"""
    task_id = str(uuid.uuid4())[:8]
    with import_tasks_lock:
        import_tasks[task_id] = {
            'status': 'pending',  # pending, running, completed, failed
            'progress': 0,
            'total': 0,
            'current': 0,
            'imported': 0,
            'skipped': 0,
            'download_failed': 0,
            'message': '准备中...',
            'created_at': time.time()
        }
    return task_id

def update_import_task(task_id, **kwargs):
    """更新导入任务状态"""
    with import_tasks_lock:
        if task_id in import_tasks:
            import_tasks[task_id].update(kwargs)

def get_import_task(task_id):
    """获取导入任务状态"""
    with import_tasks_lock:
        return import_tasks.get(task_id, {}).copy()

def cleanup_old_tasks():
    """清理超过1小时的旧任务"""
    current_time = time.time()
    with import_tasks_lock:
        to_delete = [
            task_id for task_id, task in import_tasks.items()
            if current_time - task.get('created_at', 0) > 3600
        ]
        for task_id in to_delete:
            del import_tasks[task_id]
tb_temp_dirs = {}  # 记录每个端口使用的临时目录

def get_experiment_cache_path(tb_log_path):
    """根据远程 tb_log_path 生成本地缓存路径"""
    # 使用路径的 hash 作为目录名，避免路径中的特殊字符
    path_hash = hashlib.md5(tb_log_path.encode()).hexdigest()[:12]
    # 取路径最后一部分作为可读名称
    readable_name = tb_log_path.rstrip('/').split('/')[-1]
    cache_dir_name = f"{readable_name}_{path_hash}"
    return os.path.join(get_events_cache_dir(), cache_dir_name)

def download_event_files(tb_log_path, experiment_id=None):
    """
    从远程服务器下载 TensorBoard event 文件到本地缓存
    返回本地缓存路径
    """
    config = load_config()
    
    if config['mode'] == 'local':
        # 本地模式，直接返回原路径
        return tb_log_path, True
    
    # 获取本地缓存路径
    local_cache_path = get_experiment_cache_path(tb_log_path)
    
    # 确保缓存目录存在
    if not os.path.exists(local_cache_path):
        os.makedirs(local_cache_path)
    
    remote = config['remote']
    
    # 构建 rsync 命令，添加压缩和复用连接参数
    # --compress: 传输时压缩
    # -W: 整文件传输，减少对比时间
    # --timeout=30: 30秒超时
    if config['mode'] == 'ssh_config':
        ssh_host = remote['host']
        rsync_cmd = f"rsync -avzW --compress --timeout=30 --include='*/' --include='*.tfevents*' --exclude='*' -e 'ssh -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no' {ssh_host}:{tb_log_path}/ {local_cache_path}/"
    else:
        ssh_host = f"{remote['user']}@{remote['host']}"
        port_arg = f"-p {remote['port']}" if remote.get('port', 22) != 22 else ""
        rsync_cmd = f"rsync -avzW --compress --timeout=30 --include='*/' --include='*.tfevents*' --exclude='*' -e 'ssh -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no {port_arg}' {ssh_host}:{tb_log_path}/ {local_cache_path}/"
    
    try:
        logging.info(f'下载 event 文件: {tb_log_path} -> {local_cache_path}')
        result = subprocess.run(rsync_cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            logging.warning(f'rsync 失败，尝试使用 scp: {result.stderr}')
            # rsync 失败，尝试使用 scp
            if config['mode'] == 'ssh_config':
                scp_cmd = f"scp -r -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no {ssh_host}:{tb_log_path}/* {local_cache_path}/"
            else:
                port_arg = f"-P {remote['port']}" if remote.get('port', 22) != 22 else ""
                scp_cmd = f"scp -r -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no {port_arg} {ssh_host}:{tb_log_path}/* {local_cache_path}/"
            
            result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                logging.error(f'scp 也失败: {result.stderr}')
                return None, False
        
        logging.info(f'event 文件下载成功: {local_cache_path}')
        return local_cache_path, True
        
    except subprocess.TimeoutExpired:
        logging.error(f'下载 event 文件超时: {tb_log_path}')
        return None, False
    except Exception as e:
        logging.error(f'下载 event 文件失败: {e}')
        return None, False

def extract_metadata_from_config(config_json, command_params_json=None):
    """从配置 JSON 和命令参数中提取算法、环境、地图信息"""
    algorithm = None
    environment = None
    map_name = None
    
    # 优先从命令参数中提取
    if command_params_json:
        try:
            params = json.loads(command_params_json)
            for param in params:
                if param.get('type') == 'algorithm':
                    algorithm = param.get('value')
                elif param.get('type') == 'environment':
                    environment = param.get('value')
                elif param.get('type') == 'map':
                    map_name = param.get('value')
        except (json.JSONDecodeError, TypeError):
            pass
    
    # 从配置 JSON 中提取（如果命令参数中没有）
    if config_json and (not algorithm or not environment or not map_name):
        try:
            config = json.loads(config_json)
            if not algorithm and 'alg' in config:
                algorithm = config['alg']
            if not environment and 'env' in config:
                environment = config['env']
            if not map_name and 'env_args' in config and isinstance(config['env_args'], dict):
                if 'map_name' in config['env_args']:
                    map_name = config['env_args']['map_name']
        except (json.JSONDecodeError, TypeError):
            pass
    
    return algorithm, environment, map_name

def generate_experiment_id():
    """生成唯一的实验 ID，格式：exp_YYYYMMDD_NNN"""
    today = datetime.now().strftime('%Y%m%d')
    
    # 查询今天已有的实验数量
    prefix = f'exp_{today}_'
    existing = Experiment.query.filter(Experiment.experiment_id.like(f'{prefix}%')).all()
    
    # 获取今天的最大序号
    max_num = 0
    for exp in existing:
        try:
            num = int(exp.experiment_id.split('_')[-1])
            max_num = max(max_num, num)
        except:
            pass
    
    # 生成新的 ID
    new_num = max_num + 1
    return f'{prefix}{new_num:03d}'

@api.route('/experiments', methods=['GET'])
def get_experiments():
    # 获取查询参数
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    query = Experiment.query
    
    # 搜索过滤
    if search:
        query = query.filter(Experiment.name.like(f'%{search}%'))
    if status:
        query = query.filter(Experiment.status == status)
    
    # 排序
    if sort_by == 'created_at':
        if sort_order == 'asc':
            query = query.order_by(Experiment.created_at.asc())
        else:
            query = query.order_by(Experiment.created_at.desc())
    
    # 分页
    total = query.count()
    experiments = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return jsonify({
        'experiments': [exp.to_dict() for exp in experiments],
        'total': total,
        'page': page,
        'per_page': per_page
    })

@api.route('/experiments/<int:id>', methods=['GET'])
def get_experiment(id):
    experiment = Experiment.query.get(id)
    if not experiment:
        return jsonify({'error': '实验不存在'}), 404
    return jsonify(experiment.to_dict())

@api.route('/experiments', methods=['POST'])
def create_experiment():
    data = request.json
    
    # 生成唯一的实验 ID
    experiment_id = generate_experiment_id()
    
    # 如果没有提供 tb_log_path，根据配置自动生成
    tb_log_path = data.get('tb_log_path')
    if not tb_log_path:
        config = load_config()
        if config['mode'] in ['remote', 'ssh_config']:
            base_path = config['remote'].get('tensorboard_base_path', '')
            if base_path:
                tb_log_path = f"{base_path}/{experiment_id}"
    
    # 从配置中提取元数据
    config_json = data.get('config_json')
    command_params_json = data.get('command_params_json')
    algorithm, environment, map_name = extract_metadata_from_config(config_json, command_params_json)
    
    experiment = Experiment(
        experiment_id=experiment_id,
        name=data.get('name'),
        description=data.get('description'),
        purpose=data.get('purpose'),
        status=data.get('status', 'running'),
        tags=','.join(data.get('tags', [])),
        command_params_json=data.get('command_params_json'),
        config_json=config_json,
        output_filename=data.get('output_filename'),
        algorithm=algorithm,
        environment=environment,
        map=map_name,
        tb_log_path=tb_log_path,
        tb_port=data.get('tb_port', 6006),
        results=data.get('results'),
        observations=data.get('observations'),
        conclusion=data.get('conclusion')
    )
    
    db_session.add(experiment)
    db_session.commit()
    
    return jsonify(experiment.to_dict()), 201

@api.route('/experiments/<int:id>', methods=['PUT'])
def update_experiment(id):
    experiment = Experiment.query.get(id)
    if not experiment:
        return jsonify({'error': '实验不存在'}), 404
    
    data = request.json
    
    # 如果更新了 config_json 或 command_params_json，重新提取元数据
    if 'config_json' in data or 'command_params_json' in data:
        config_json = data.get('config_json', experiment.config_json)
        command_params_json = data.get('command_params_json', experiment.command_params_json)
        algorithm, environment, map_name = extract_metadata_from_config(config_json, command_params_json)
        
        if 'config_json' in data:
            experiment.config_json = config_json
        if 'command_params_json' in data:
            experiment.command_params_json = command_params_json
            
        experiment.algorithm = algorithm
        experiment.environment = environment
        experiment.map = map_name
    
    # 允许直接更新 algorithm、environment、map 字段（用于批量编辑）
    if 'algorithm' in data:
        experiment.algorithm = data['algorithm']
    if 'environment' in data:
        experiment.environment = data['environment']
    if 'map' in data:
        experiment.map = data['map']
    
    experiment.name = data.get('name', experiment.name)
    experiment.description = data.get('description', experiment.description)
    experiment.purpose = data.get('purpose', experiment.purpose)
    experiment.status = data.get('status', experiment.status)
    experiment.tags = ','.join(data.get('tags', [])) if 'tags' in data else experiment.tags
    experiment.output_filename = data.get('output_filename', experiment.output_filename)
    experiment.tb_log_path = data.get('tb_log_path', experiment.tb_log_path)
    experiment.tb_port = data.get('tb_port', experiment.tb_port)
    experiment.results = data.get('results', experiment.results)
    experiment.observations = data.get('observations', experiment.observations)
    experiment.conclusion = data.get('conclusion', experiment.conclusion)
    
    db_session.commit()
    
    return jsonify(experiment.to_dict())

@api.route('/experiments/<int:id>', methods=['DELETE'])
def delete_experiment(id):
    experiment = Experiment.query.get(id)
    if not experiment:
        return jsonify({'error': '实验不存在'}), 404
    
    db_session.delete(experiment)
    db_session.commit()
    
    return jsonify({'message': '删除成功'})

@api.route('/tensorboard/start', methods=['POST'])
def start_tensorboard():
    data = request.json
    log_path = data.get('log_path')
    log_paths = data.get('log_paths')  # 支持多个日志路径
    experiment_names = data.get('experiment_names')  # 实验名称列表（可选）
    port = data.get('port', 6006)
    local_cache_path = data.get('local_cache_path')  # 单个本地缓存路径
    local_cache_paths = data.get('local_cache_paths')  # 多个本地缓存路径
    
    config = load_config()
    local_tb_config = config.get('local_tensorboard', {})
    use_local_tb = local_tb_config.get('enabled', True)
    local_tb_cmd = local_tb_config.get('command', 'tensorboard')
    
    # 检查是否已经在运行
    if port in tb_processes and tb_processes[port].poll() is None:
        # 如果已经在运行，先停止它
        try:
            process = tb_processes[port]
            process.terminate()
            process.wait(timeout=5)
            del tb_processes[port]
            logging.info(f'已停止端口 {port} 上的旧 TensorBoard 进程')
        except Exception as e:
            logging.warning(f'停止旧进程失败: {e}')
    
    # 判断是否可以使用本地 TensorBoard
    # 条件：启用了本地 TensorBoard，并且有本地缓存路径
    can_use_local = False
    local_paths_to_use = []
    
    if use_local_tb:
        if local_cache_paths:
            # 多个实验，检查是否所有实验都有本地缓存
            logging.info(f'批量启动：接收到 {len(local_cache_paths)} 个本地缓存路径')
            for idx, p in enumerate(local_cache_paths):
                logging.info(f'  路径 [{idx+1}]: {p} (存在: {os.path.exists(p) if p else False})')
            
            valid_paths = [p for p in local_cache_paths if p and os.path.exists(p)]
            if len(valid_paths) == len(local_cache_paths):
                can_use_local = True
                local_paths_to_use = valid_paths
                logging.info(f'使用本地缓存启动 TensorBoard (多个实验): {len(valid_paths)} 个')
            elif len(valid_paths) > 0:
                # 部分有缓存，也使用本地
                can_use_local = True
                local_paths_to_use = valid_paths
                logging.info(f'部分实验有本地缓存，使用 {len(valid_paths)}/{len(local_cache_paths)} 个')
            else:
                logging.warning('所有本地缓存路径都不存在或为空')
        elif local_cache_path and os.path.exists(local_cache_path):
            # 单个实验有本地缓存
            can_use_local = True
            local_paths_to_use = [local_cache_path]
            logging.info(f'使用本地缓存启动 TensorBoard: {local_cache_path}')
    
    # 如果可以使用本地 TensorBoard
    if can_use_local and local_paths_to_use:
        try:
            # 检查本地是否安装了 tensorboard
            check_tb_cmd = f"which {local_tb_cmd}"
            tb_check_result = subprocess.run(check_tb_cmd, shell=True, capture_output=True, text=True)
            
            if tb_check_result.returncode != 0:
                # 本地没有安装 tensorboard
                logging.warning(f'本地未安装 TensorBoard ({local_tb_cmd})，回退到远程模式')
                can_use_local = False
            else:
                # 构建本地 TensorBoard 命令
                if len(local_paths_to_use) == 1:
                    logdir = local_paths_to_use[0]
                    logging.info(f'单个本地缓存路径: {logdir}')
                else:
                    # 多个路径，创建临时目录并建立符号链接
                    logging.info(f'检测到多个本地缓存路径: {len(local_paths_to_use)} 个')
                    timestamp = int(time.time())
                    paths_hash = hashlib.md5(','.join(sorted(local_paths_to_use)).encode()).hexdigest()[:8]
                    temp_dir = f'/tmp/tensorboard_local_{timestamp}_{paths_hash}'
                    os.makedirs(temp_dir, exist_ok=True)
                    logging.info(f'创建临时目录: {temp_dir}')
                    
                    for i, path in enumerate(local_paths_to_use):
                        if experiment_names and i < len(experiment_names):
                            link_name = experiment_names[i].replace('/', '_').replace(' ', '_').replace("'", "")
                        else:
                            link_name = os.path.basename(path)
                        link_path = os.path.join(temp_dir, link_name)
                        if os.path.exists(link_path):
                            os.remove(link_path)
                        os.symlink(path, link_path)
                        logging.info(f'创建符号链接 [{i+1}/{len(local_paths_to_use)}]: {link_name} -> {path}')
                    
                    logdir = temp_dir
                    tb_temp_dirs[port] = (temp_dir, 'local')
                    logging.info(f'所有符号链接创建完成，TensorBoard logdir: {logdir}')
                
                cmd = f"{local_tb_cmd} --logdir={logdir} --port={port}"
                logging.info(f'启动本地 TensorBoard: {cmd}')
                
                process = subprocess.Popen(cmd, shell=True)
                tb_processes[port] = process
                
                # 短暂等待 TensorBoard 启动
                time.sleep(2)
                
                # 立即打开浏览器
                webbrowser.open(f"http://localhost:{port}")
                
                return jsonify({
                    'message': '本地 TensorBoard 启动成功',
                    'url': f'http://localhost:{port}',
                    'mode': 'local'
                })
        except Exception as e:
            logging.error(f'启动本地 TensorBoard 失败: {e}')
            # 本地失败，回退到远程模式
            can_use_local = False
    
    # 如果不能使用本地 TensorBoard，则使用远程模式
    # 如果提供了多个日志路径，合并它们
    if log_paths:
        # 记录日志用于调试
        logging.info(f'批量启动 TensorBoard')
        logging.info(f'路径数量: {len(log_paths)}')
        
        # 如果只有一个路径，直接使用该路径
        if len(log_paths) == 1:
            log_path = log_paths[0]
            logging.info(f'只有一个路径，直接使用: {log_path}')
        else:
            # 多个路径时，创建临时目录并使用符号链接
            
            # 生成一个唯一的临时目录名
            timestamp = int(time.time())
            paths_hash = hashlib.md5(','.join(sorted(log_paths)).encode()).hexdigest()[:8]
            temp_dir = f'/tmp/tensorboard_compare_{timestamp}_{paths_hash}'
            
            # 如果是远程模式，在远程服务器上创建临时目录和符号链接
            if config['mode'] in ['remote', 'ssh_config']:
                remote = config['remote']
                if config['mode'] == 'ssh_config':
                    ssh_host_for_link = remote['host']
                    ssh_cmd_prefix = f"ssh -o ConnectTimeout=10 {ssh_host_for_link}"
                else:
                    ssh_host_for_link = f"{remote['user']}@{remote['host']}"
                    port_arg = f"-p {remote['port']}" if remote.get('port', 22) != 22 else ""
                    ssh_cmd_prefix = f"ssh -o ConnectTimeout=10 {port_arg} {ssh_host_for_link}".strip()
                
                # 构建一条命令完成所有操作：创建目录 + 所有符号链接
                link_commands = [f'mkdir -p {temp_dir}']
                for i, path in enumerate(log_paths):
                    # 使用实验名称或路径的最后部分作为链接名
                    if experiment_names and i < len(experiment_names):
                        link_name = experiment_names[i].replace('/', '_').replace(' ', '_').replace("'", "")
                    else:
                        link_name = path.rstrip('/').split('/')[-1]
                    link_commands.append(f'ln -sf "{path}" "{temp_dir}/{link_name}"')
                
                # 用 && 连接所有命令，一次 SSH 调用完成
                all_commands = ' && '.join(link_commands)
                batch_cmd = f"{ssh_cmd_prefix} '{all_commands}'"
                try:
                    subprocess.run(batch_cmd, shell=True, timeout=30)
                    logging.info(f'一次性创建 {len(log_paths)} 个符号链接')
                except subprocess.TimeoutExpired:
                    return jsonify({'error': 'SSH 连接超时，请检查网络连接或 SSH 配置'}), 500
                
                log_path = temp_dir
                
                # 记录临时目录，以便停止时清理
                tb_temp_dirs[port] = (temp_dir, ssh_host_for_link)
            else:
                # 本地模式
                log_path = ','.join(log_paths)
                logging.info(f'本地模式，使用逗号分隔: {log_path}')
    else:
        logging.info(f'单个实验启动 TensorBoard')
        logging.info(f'日志路径: {log_path}')
    
    try:
        if config['mode'] == 'remote' or config['mode'] == 'ssh_config':
            # 远程模式或 SSH Config 模式：通过 SSH 启动 TensorBoard
            remote = config['remote']
            tensorboard_cmd = remote.get('tensorboard_cmd', '')
            
            if not tensorboard_cmd:
                return jsonify({'error': '请先在系统设置中配置 TensorBoard 命令路径'}), 400
            
            # 构建 TensorBoard 启动命令
            tb_start_cmd = f"{tensorboard_cmd} --logdir={log_path} --port={port} --host 0.0.0.0"
            
            # 确定 SSH 主机和端口参数
            if config['mode'] == 'ssh_config':
                # SSH Config 模式：使用配置的主机别名
                ssh_host = remote['host']
                ssh_prefix = f"ssh {ssh_host}"
                ssh_cmd = f"ssh -f -N -L {port}:localhost:{port} {ssh_host}"
            else:
                # 远程模式：使用用户名@主机
                ssh_host = f"{remote['user']}@{remote['host']}"
                port_arg = f"-p {remote['port']}" if remote.get('port', 22) != 22 else ""
                ssh_prefix = f"ssh {port_arg} {ssh_host}".strip()
                ssh_cmd = f"ssh -f -N -L {port}:localhost:{port} {port_arg} {ssh_host}"
            
            # 本地清理 SSH 隧道（异步执行）
            cleanup_tunnel_cmd = f"pkill -f 'ssh.*-L {port}:localhost:{port}' 2>/dev/null || true"
            subprocess.Popen(cleanup_tunnel_cmd, shell=True)
            
            # 远程清理旧 TensorBoard 并启动新的
            # 先清理旧进程（增加超时时间，使用 -o ConnectTimeout 避免长时间等待）
            cleanup_cmd = f"{ssh_prefix} -o ConnectTimeout=10 'pkill -f \"tensorboard.*--port={port}\" 2>/dev/null || true'"
            try:
                subprocess.run(cleanup_cmd, shell=True, timeout=15)
            except subprocess.TimeoutExpired:
                logging.warning(f'清理旧 TensorBoard 进程超时，继续尝试启动')
            
            # 启动新的 TensorBoard（使用 nohup 后台运行）
            start_cmd = f"{ssh_prefix} -o ConnectTimeout=10 'nohup {tb_start_cmd} > /tmp/tensorboard_{port}.log 2>&1 &'"
            subprocess.run(start_cmd, shell=True, timeout=15)
            
            # 建立 SSH 隧道
            process = subprocess.Popen(ssh_cmd, shell=True)
            tb_processes[port] = process
            
            # 等待 TensorBoard 启动和隧道建立
            time.sleep(1.5)
            
            # 快速检查远程 TensorBoard 是否启动
            check_cmd = f"{ssh_prefix} -o ConnectTimeout=10 'pgrep -f \"tensorboard.*--port={port}\" >/dev/null && echo ok || echo fail'"
            try:
                check_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=15)
                if 'ok' not in check_result.stdout:
                    # 如果没有启动成功，读取日志
                    log_cmd = f"{ssh_prefix} -o ConnectTimeout=10 'tail -20 /tmp/tensorboard_{port}.log 2>/dev/null || echo \"无日志文件\"'"
                    log_result = subprocess.run(log_cmd, shell=True, capture_output=True, text=True, timeout=15)
                    error_msg = f'TensorBoard 启动失败。请检查 TensorBoard 命令路径是否正确。日志: {log_result.stdout}'
                    return jsonify({'error': error_msg}), 500
            except subprocess.TimeoutExpired:
                logging.warning(f'检查 TensorBoard 状态超时，假设启动成功')
            
            message = f'远程 TensorBoard 启动成功 (通过 SSH 隧道)'
        else:
            # 本地模式
            # 如果是多个路径（用逗号分隔），不检查路径是否存在
            # TensorBoard 会自动处理不存在的路径
            if not log_path:
                return jsonify({'error': '日志路径不能为空'}), 400
            
            # 如果是单个路径，检查是否存在
            if ',' not in log_path and not os.path.exists(log_path):
                return jsonify({'error': f'日志路径不存在: {log_path}'}), 400
            
            cmd = f"tensorboard --logdir={log_path} --port={port}"
            process = subprocess.Popen(cmd, shell=True)
            tb_processes[port] = process
            
            # 短暂等待 TensorBoard 启动
            time.sleep(1)
            message = 'TensorBoard 启动成功'
        
        # 立即打开浏览器（TensorBoard 会自动加载）
        webbrowser.open(f"http://localhost:{port}")
        
        return jsonify({
            'message': message,
            'pid': process.pid if 'process' in locals() else None,
            'port': port,
            'url': f"http://localhost:{port}"
        })
    except Exception as e:
        return jsonify({'error': f'启动失败: {str(e)}'}), 500

@api.route('/tensorboard/stop', methods=['POST'])
def stop_tensorboard():
    data = request.json
    port = data.get('port', 6006)
    
    if port not in tb_processes:
        return jsonify({'error': '未找到运行中的 TensorBoard'}), 404
    
    try:
        process = tb_processes[port]
        process.terminate()
        process.wait(timeout=5)
        del tb_processes[port]
        
        # 清理临时目录（如果有）
        if port in tb_temp_dirs:
            temp_dir, ssh_host = tb_temp_dirs[port]
            if ssh_host == 'local':
                # 本地临时目录
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            else:
                # 远程临时目录
                cleanup_cmd = f"ssh {ssh_host} 'rm -rf {temp_dir}'"
                subprocess.run(cleanup_cmd, shell=True)
            del tb_temp_dirs[port]
            logging.info(f'已清理临时目录: {temp_dir}')
        
        return jsonify({'message': 'TensorBoard 已停止'})
    except Exception as e:
        return jsonify({'error': f'停止失败: {str(e)}'}), 500

@api.route('/tensorboard/status', methods=['GET'])
def tensorboard_status():
    port = int(request.args.get('port', 6006))
    
    if port in tb_processes and tb_processes[port].poll() is None:
        return jsonify({
            'running': True,
            'pid': tb_processes[port].pid,
            'port': port
        })
    else:
        return jsonify({'running': False})

@api.route('/tags', methods=['GET'])
def get_tags():
    experiments = Experiment.query.all()
    tags_set = set()
    
    for exp in experiments:
        if exp.tags:
            tags_set.update(exp.tags.split(','))
    
    return jsonify(list(tags_set))

@api.route('/export', methods=['POST'])
def export_data():
    experiments = Experiment.query.all()
    data = [exp.to_dict() for exp in experiments]
    return jsonify(data)

@api.route('/config', methods=['GET'])
def get_config():
    """获取服务器配置"""
    return jsonify(load_config())

@api.route('/config', methods=['POST'])
def update_config():
    """更新服务器配置"""
    data = request.json
    save_config(data)
    return jsonify({'message': '配置已保存'})

@api.route('/scan-experiments', methods=['POST'])
def scan_experiments():
    """扫描远程服务器的 TensorBoard 日志目录"""
    config = load_config()
    
    if config['mode'] == 'local':
        return jsonify({'error': '本地模式不支持扫描'}), 400
    
    remote = config['remote']
    base_path = remote.get('tensorboard_base_path', '')
    
    if not base_path:
        return jsonify({'error': '请先在系统设置中配置 TensorBoard 基础路径'}), 400
    
    try:
        # 构建 SSH 命令
        if config['mode'] == 'ssh_config':
            ssh_host = remote['host']
        else:
            ssh_host = f"{remote['user']}@{remote['host']}"
            if remote.get('port', 22) != 22:
                ssh_host = f"-p {remote['port']} {ssh_host}"
        
        # 扫描目录，查找包含 events.out.tfevents 的子目录，同时获取修改时间
        # 使用一条命令同时获取路径和时间，大幅提升速度
        cmd = f"ssh {ssh_host} 'find {base_path} -type f -name \"events.out.tfevents*\" -printf \"%h %T@\\n\" | sort -u -k1,1'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return jsonify({'error': f'扫描失败: {result.stderr}'}), 500
        
        # 解析结果（每行格式: "路径 时间戳"）
        lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        
        # 用字典去重，保留每个目录的最新时间戳
        dir_timestamps = {}
        for line in lines:
            parts = line.rsplit(' ', 1)  # 从右边分割，只分割一次
            if len(parts) == 2:
                log_dir, ts = parts
                try:
                    timestamp = int(float(ts))
                    # 保留最新的时间戳
                    if log_dir not in dir_timestamps or timestamp > dir_timestamps[log_dir]:
                        dir_timestamps[log_dir] = timestamp
                except:
                    dir_timestamps[log_dir] = None
            else:
                dir_timestamps[line] = None
        
        experiments = []
        for log_dir, timestamp in dir_timestamps.items():
            # 提取实验名称（相对于基础路径）
            rel_path = log_dir.replace(base_path, '').strip('/')
            if not rel_path:
                continue
            
            # 尝试从路径中提取算法、环境、地图信息
            algorithm = ''
            environment = ''
            map_name = ''
            
            # 从路径中提取（通常路径格式类似：map__env__alg__timestamp）
            path_parts = rel_path.split('/')
            path_name = path_parts[-1] if path_parts else rel_path
            
            # 尝试按双下划线分割
            if '__' in path_name:
                parts = path_name.split('__')
                # 尝试识别每个部分是什么
                for part in parts:
                    part_lower = part.lower()
                    # 识别算法
                    if any(alg in part_lower for alg in ['qmix', 'vdn', 'iql', 'qtran', 'coma', 'maven']):
                        if not algorithm:
                            algorithm = part
                    # 识别环境
                    elif 'sc2' in part_lower or 'smac' in part_lower:
                        if not environment:
                            environment = part
                    # 识别地图
                    elif any(m in part_lower for m in ['mmm', '2s3z', '3s5z', '8m', '5m_vs_6m', 'corridor', '3s_vs_5z', '2s_vs_1sc']):
                        if not map_name:
                            map_name = part
            
            # 如果没有提取到，尝试从整个路径中查找关键词
            if not algorithm or not environment or not map_name:
                path_lower = rel_path.lower()
                
                # 提取算法
                if not algorithm:
                    for alg in ['qmix', 'vdn', 'iql', 'qtran', 'coma', 'maven']:
                        if alg in path_lower:
                            algorithm = alg.upper()
                            break
                
                # 提取环境
                if not environment:
                    if 'sc2' in path_lower or 'smac' in path_lower:
                        environment = 'sc2'
                
                # 提取地图
                if not map_name:
                    for map_pattern in ['mmm2', 'mmm', '2s3z', '3s5z', '8m', '5m_vs_6m', 'corridor', '3s_vs_5z', '2s_vs_1sc']:
                        if map_pattern in path_lower:
                            # 找到地图名称的完整部分
                            for part in path_name.split('__'):
                                if map_pattern in part.lower():
                                    map_name = part
                                    break
                            if not map_name:
                                map_name = map_pattern.upper()
                            break
            
            experiments.append({
                'name': rel_path.replace('/', '_'),
                'tb_log_path': log_dir,
                'relative_path': rel_path,
                'timestamp': timestamp,
                'algorithm': algorithm,
                'environment': environment,
                'map': map_name
            })
        
        return jsonify({
            'experiments': experiments,
            'total': len(experiments),
            'base_path': base_path
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': '扫描超时，请检查网络连接'}), 500
    except Exception as e:
        return jsonify({'error': f'扫描失败: {str(e)}'}), 500

@api.route('/import-experiments', methods=['POST'])
def import_experiments():
    """批量导入实验 - 异步执行，立即返回任务ID"""
    data = request.json
    experiments_data = data.get('experiments', [])
    download_events = data.get('download_events', True)
    
    if not experiments_data:
        return jsonify({'error': '没有要导入的实验'}), 400
    
    # 清理旧任务
    cleanup_old_tasks()
    
    # 创建新任务
    task_id = create_import_task()
    update_import_task(task_id, 
                       status='running',
                       total=len(experiments_data),
                       message=f'正在检查 {len(experiments_data)} 个实验...')
    
    # 在后台线程执行导入
    def run_import():
        try:
            _execute_import_task(task_id, experiments_data, download_events)
        except Exception as e:
            logging.error(f'导入任务异常: {e}')
            update_import_task(task_id, 
                             status='failed',
                             message=f'导入失败: {str(e)}')
    
    thread = threading.Thread(target=run_import, daemon=True)
    thread.start()
    
    return jsonify({
        'task_id': task_id,
        'message': '导入任务已启动'
    })

def _execute_import_task(task_id, experiments_data, download_events):
    """实际执行导入任务的函数（在后台线程中运行）"""
    from app import app
    
    with app.app_context():
        config = load_config()
        use_local_tb = config.get('local_tensorboard', {}).get('enabled', True)
        
        # 先批量查询已存在的实验路径
        update_import_task(task_id, message='检查已存在的实验...')
        
        existing_paths = set()
        all_paths = [exp['tb_log_path'] for exp in experiments_data]
        existing_experiments = Experiment.query.filter(Experiment.tb_log_path.in_(all_paths)).all()
        for exp in existing_experiments:
            existing_paths.add(exp.tb_log_path)
        
        # 筛选需要导入的实验
        to_import = []
        skipped = len(existing_paths)
        
        for exp_data in experiments_data:
            if exp_data['tb_log_path'] not in existing_paths:
                to_import.append(exp_data)
        
        if not to_import:
            update_import_task(task_id,
                             status='completed',
                             progress=100,
                             imported=0,
                             skipped=skipped,
                             message=f'跳过 {skipped} 个已存在的实验，没有新实验需要导入')
            return
        
        total_to_import = len(to_import)
        update_import_task(task_id,
                         total=total_to_import,
                         skipped=skipped,
                         message=f'准备导入 {total_to_import} 个实验...')
        
        # 并行下载 event 文件
        download_results = {}
        download_failed = 0
        downloaded_count = 0
        
        if download_events and use_local_tb and config['mode'] != 'local':
            update_import_task(task_id, message=f'正在下载 event 文件 (0/{total_to_import})...')
            
            max_workers = min(8, total_to_import)
            
            def download_task(exp_data):
                tb_log_path = exp_data['tb_log_path']
                cache_path, success = download_event_files(tb_log_path)
                return tb_log_path, cache_path, success
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(download_task, exp): exp for exp in to_import}
                for future in as_completed(futures):
                    try:
                        tb_log_path, cache_path, success = future.result()
                        if success:
                            download_results[tb_log_path] = cache_path
                        else:
                            download_results[tb_log_path] = None
                            download_failed += 1
                    except Exception as e:
                        logging.error(f'下载任务异常: {e}')
                        exp = futures[future]
                        download_results[exp['tb_log_path']] = None
                        download_failed += 1
                    
                    # 更新进度
                    downloaded_count += 1
                    progress = int((downloaded_count / total_to_import) * 70)  # 下载占70%进度
                    update_import_task(task_id,
                                     current=downloaded_count,
                                     progress=progress,
                                     download_failed=download_failed,
                                     message=f'正在下载 event 文件 ({downloaded_count}/{total_to_import})...')
        else:
            # 不需要下载，直接标记为已完成下载阶段
            update_import_task(task_id, 
                             progress=70,
                             message='准备保存实验记录...')
        
        # 批量创建实验记录
        update_import_task(task_id, 
                         progress=75,
                         message='正在保存实验记录...')
        
        imported = 0
        for idx, exp_data in enumerate(to_import):
            created_time = None
            if exp_data.get('timestamp'):
                created_time = datetime.fromtimestamp(exp_data['timestamp'])
            
            experiment_id = generate_experiment_id()
            
            local_cache_path = download_results.get(exp_data['tb_log_path'])
            if download_events and use_local_tb and config['mode'] != 'local' and local_cache_path is None:
                if exp_data['tb_log_path'] not in download_results:
                    download_failed += 1
                logging.warning(f'下载 event 文件失败: {exp_data["tb_log_path"]}')
            
            experiment = Experiment(
                experiment_id=experiment_id,
                name=exp_data.get('name', '未命名实验'),
                description=exp_data.get('description', ''),
                status='completed',
                tb_log_path=exp_data['tb_log_path'],
                tb_local_cache_path=local_cache_path,
                tb_port=6006,
                algorithm=exp_data.get('algorithm', ''),
                environment=exp_data.get('environment', ''),
                map=exp_data.get('map', ''),
                created_at=created_time,
                updated_at=created_time
            )
            
            db_session.add(experiment)
            imported += 1
            
            # 更新保存进度 (75% -> 95%)
            save_progress = 75 + int(((idx + 1) / total_to_import) * 20)
            update_import_task(task_id,
                             progress=save_progress,
                             current=imported,
                             imported=imported)
        
        db_session.commit()
        
        # 完成
        message = f'成功导入 {imported} 个实验'
        if skipped > 0:
            message += f'，跳过 {skipped} 个已存在的实验'
        if download_failed > 0:
            message += f'，{download_failed} 个实验的 event 文件下载失败'
        
        update_import_task(task_id,
                         status='completed',
                         progress=100,
                         imported=imported,
                         skipped=skipped,
                         download_failed=download_failed,
                         message=message)

@api.route('/import-status/<task_id>', methods=['GET'])
def get_import_status(task_id):
    """查询导入任务状态"""
    task = get_import_task(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    return jsonify(task)

# ==================== 附件上传/下载 API ====================

# 确保上传目录存在
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@api.route('/experiments/<int:id>/attachments', methods=['POST'])
def upload_attachment(id):
    """上传附件（CSV 文件）"""
    experiment = Experiment.query.get(id)
    if not experiment:
        return jsonify({'error': '实验不存在'}), 404
    
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    # 只允许 CSV 文件
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': '只支持 CSV 文件'}), 400
    
    # 生成唯一文件名
    import uuid
    original_filename = file.filename
    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
    
    # 创建实验专属目录
    exp_folder = os.path.join(UPLOAD_FOLDER, str(id))
    if not os.path.exists(exp_folder):
        os.makedirs(exp_folder)
    
    # 保存文件
    file_path = os.path.join(exp_folder, unique_filename)
    file.save(file_path)
    
    # 返回附件信息
    attachment_info = {
        'id': unique_filename,
        'name': original_filename,
        'size': os.path.getsize(file_path),
        'uploaded_at': datetime.now().isoformat()
    }
    
    return jsonify(attachment_info)

@api.route('/experiments/<int:id>/attachments/<attachment_id>', methods=['GET'])
def download_attachment(id, attachment_id):
    """下载附件"""
    from flask import send_file
    
    experiment = Experiment.query.get(id)
    if not experiment:
        return jsonify({'error': '实验不存在'}), 404
    
    exp_folder = os.path.join(UPLOAD_FOLDER, str(id))
    file_path = os.path.join(exp_folder, attachment_id)
    
    if not os.path.exists(file_path):
        return jsonify({'error': '附件不存在'}), 404
    
    # 从文件名中提取原始文件名
    original_filename = '_'.join(attachment_id.split('_')[1:])
    
    return send_file(file_path, as_attachment=True, download_name=original_filename)

@api.route('/experiments/<int:id>/attachments/<attachment_id>', methods=['DELETE'])
def delete_attachment(id, attachment_id):
    """删除附件"""
    experiment = Experiment.query.get(id)
    if not experiment:
        return jsonify({'error': '实验不存在'}), 404
    
    exp_folder = os.path.join(UPLOAD_FOLDER, str(id))
    file_path = os.path.join(exp_folder, attachment_id)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return jsonify({'message': '删除成功'})

@api.route('/generate-experiment-id', methods=['GET'])
def generate_experiment_id_api():
    """生成实验 ID（用于预览）"""
    experiment_id = generate_experiment_id()
    return jsonify({
        'experiment_id': experiment_id
    })

@api.route('/generate-command', methods=['POST'])
def generate_command():
    """生成运行命令"""
    data = request.json
    experiment_id = data.get('experiment_id', 'exp_YYYYMMDD_NNN')
    command_params = data.get('command_params', [])  # 命令参数列表
    config_json = data.get('config_json', '')
    output_filename = data.get('output_filename', '')  # 自定义输出文件名
    tb_log_path = data.get('tb_log_path', '')
    
    # 获取配置
    config = load_config()
    
    # 从命令参数中提取地图名（用于生成输出文件名）
    map_name = ''
    for param in command_params:
        if param.get('type') == 'map' and param.get('value'):
            map_name = param['value']
            break
    
    # 构建输出文件名
    if output_filename:
        # 使用用户自定义的文件名
        output_file = f"{output_filename}.out"
    else:
        # 使用默认格式：实验ID_地图名_train.out
        output_file = f"{experiment_id}"
        if map_name:
            output_file += f"_{map_name}"
        output_file += "_train.out"
    
    # 构建命令
    command_parts = ["nohup python3 -u src/main.py"]
    
    # 添加命令参数（-- 开头的参数，只添加启用的参数）
    for param in command_params:
        if not param.get('enabled', True):
            continue  # 跳过未启用的参数
        param_name = param.get('name', '')
        param_value = param.get('value', '')
        if param_name and param_value:
            command_parts.append(f"--{param_name}={param_value}")
    
    # 构建 with 参数部分
    with_params = []
    
    # 先添加用户配置的参数
    if config_json:
        try:
            import json
            params = json.loads(config_json)
            for key, value in params.items():
                # 处理不同类型的值
                if isinstance(value, str):
                    with_params.append(f"{key}={value}")
                elif isinstance(value, bool):
                    with_params.append(f"{key}={'True' if value else 'False'}")
                else:
                    with_params.append(f"{key}={value}")
        except:
            pass
    
    # 最后添加 TensorBoard 日志路径（如果提供）
    if tb_log_path:
        # 获取配置的 TensorBoard 参数名称
        config = load_config()
        tb_param_name = config.get('remote', {}).get('tensorboard_param_name', 'local_results_path')
        
        with_params.append(f"{tb_param_name}={tb_log_path}")
    
    # 添加 with 参数
    if with_params:
        command_parts.append("with")
        # 每个 with 参数单独一行
        for param in with_params:
            command_parts.append(f"  {param}")
    
    # 构建完整命令（换行显示）
    command = " \\\n  ".join(command_parts)
    command += f" \\\n  &> {output_file} &"
    
    return jsonify({
        'command': command,
        'experiment_id': experiment_id,
        'tb_log_path': tb_log_path
    })

# ==================== 实验组 API ====================

@api.route('/groups', methods=['GET'])
def get_groups():
    """获取所有实验组（支持分页）"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    query = ExperimentGroup.query
    
    # 排序
    if sort_by == 'created_at':
        if sort_order == 'asc':
            query = query.order_by(ExperimentGroup.created_at.asc())
        else:
            query = query.order_by(ExperimentGroup.created_at.desc())
    
    # 分页
    total = query.count()
    groups = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return jsonify({
        'groups': [group.to_dict() for group in groups],
        'total': total,
        'page': page,
        'per_page': per_page
    })

@api.route('/groups/<int:id>', methods=['GET'])
def get_group(id):
    """获取实验组详情"""
    group = ExperimentGroup.query.get(id)
    if not group:
        return jsonify({'error': '实验组不存在'}), 404
    return jsonify(group.to_dict(include_experiments=True))

@api.route('/groups', methods=['POST'])
def create_group():
    """创建实验组"""
    data = request.json
    
    group = ExperimentGroup(
        name=data.get('name'),
        description=data.get('description'),
        purpose=data.get('purpose'),
        observations=data.get('observations'),
        conclusion=data.get('conclusion')
    )
    
    # 添加实验到组
    experiment_ids = data.get('experiment_ids', [])
    if experiment_ids:
        experiments = Experiment.query.filter(Experiment.id.in_(experiment_ids)).all()
        group.experiments = experiments
    
    db_session.add(group)
    db_session.commit()
    
    return jsonify(group.to_dict(include_experiments=True)), 201

@api.route('/groups/<int:id>', methods=['PUT'])
def update_group(id):
    """更新实验组"""
    group = ExperimentGroup.query.get(id)
    if not group:
        return jsonify({'error': '实验组不存在'}), 404
    
    data = request.json
    
    group.name = data.get('name', group.name)
    group.description = data.get('description', group.description)
    group.purpose = data.get('purpose', group.purpose)
    group.observations = data.get('observations', group.observations)
    group.conclusion = data.get('conclusion', group.conclusion)
    
    # 更新实验列表
    if 'experiment_ids' in data:
        experiment_ids = data['experiment_ids']
        experiments = Experiment.query.filter(Experiment.id.in_(experiment_ids)).all()
        group.experiments = experiments
    
    db_session.commit()
    
    return jsonify(group.to_dict(include_experiments=True))

@api.route('/groups/<int:id>', methods=['DELETE'])
def delete_group(id):
    """删除实验组"""
    group = ExperimentGroup.query.get(id)
    if not group:
        return jsonify({'error': '实验组不存在'}), 404
    
    db_session.delete(group)
    db_session.commit()
    
    return jsonify({'message': '删除成功'})

@api.route('/groups/<int:id>/experiments', methods=['POST'])
def add_experiments_to_group(id):
    """向实验组添加实验"""
    group = ExperimentGroup.query.get(id)
    if not group:
        return jsonify({'error': '实验组不存在'}), 404
    
    data = request.json
    experiment_ids = data.get('experiment_ids', [])
    
    experiments = Experiment.query.filter(Experiment.id.in_(experiment_ids)).all()
    
    # 添加新实验（避免重复）
    for exp in experiments:
        if exp not in group.experiments:
            group.experiments.append(exp)
    
    db_session.commit()
    
    return jsonify(group.to_dict(include_experiments=True))

@api.route('/groups/<int:id>/experiments/<int:exp_id>', methods=['DELETE'])
def remove_experiment_from_group(id, exp_id):
    """从实验组移除实验"""
    group = ExperimentGroup.query.get(id)
    if not group:
        return jsonify({'error': '实验组不存在'}), 404
    
    experiment = Experiment.query.get(exp_id)
    if not experiment:
        return jsonify({'error': '实验不存在'}), 404
    
    if experiment in group.experiments:
        group.experiments.remove(experiment)
        db_session.commit()
    
    return jsonify(group.to_dict(include_experiments=True))
