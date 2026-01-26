import os
import json

CONFIG_FILE = 'server_config.json'

# 本地 TensorBoard 事件文件缓存目录
EVENTS_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'events_cache')

def get_events_cache_dir():
    """获取事件文件缓存目录，如果不存在则创建"""
    if not os.path.exists(EVENTS_CACHE_DIR):
        os.makedirs(EVENTS_CACHE_DIR)
    return EVENTS_CACHE_DIR

def load_config():
    """加载服务器配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 确保有本地 TensorBoard 配置
            if 'local_tensorboard' not in config:
                config['local_tensorboard'] = {
                    'enabled': True,
                    'command': 'tensorboard'  # 默认使用系统 tensorboard
                }
            return config
    return {
        'mode': 'local',  # 'local' 或 'remote'
        'remote': {
            'host': '',
            'user': '',
            'port': 22,
            'tensorboard_base_path': ''  # 远程服务器上的 tb 目录路径
        },
        'local_tensorboard': {
            'enabled': True,
            'command': 'tensorboard'
        }
    }

def save_config(config):
    """保存服务器配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
