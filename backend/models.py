from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# 实验组和实验的多对多关联表
group_experiments = Table(
    'group_experiments',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('experiment_groups.id'), primary_key=True),
    Column('experiment_id', Integer, ForeignKey('experiments.id'), primary_key=True),
    Column('added_at', DateTime, default=datetime.now)
)

class ExperimentGroup(Base):
    __tablename__ = 'experiment_groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    purpose = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 组级别的笔记
    observations = Column(Text)
    conclusion = Column(Text)
    
    # 关联的实验
    experiments = relationship('Experiment', secondary=group_experiments, backref='groups')
    
    def to_dict(self, include_experiments=False):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'purpose': self.purpose,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'observations': self.observations,
            'conclusion': self.conclusion,
            'experiment_count': len(self.experiments)
        }
        
        if include_experiments:
            result['experiments'] = [exp.to_dict() for exp in self.experiments]
        
        return result

class Experiment(Base):
    __tablename__ = 'experiments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(String(50), unique=True, nullable=False)  # 唯一的实验标识符
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    description = Column(Text)
    purpose = Column(Text)
    status = Column(String(50), default='running')
    tags = Column(String(500))
    
    # 实验配置
    command_params_json = Column(Text)  # 命令参数 JSON
    config_json = Column(Text)  # with 参数 JSON
    output_filename = Column(String(200))  # 输出文件名（不含 .out 后缀）
    
    # 实验元数据（从配置中提取）
    algorithm = Column(String(100))  # 算法名称
    environment = Column(String(100))  # 环境名称
    map = Column(String(100))  # 地图名称
    
    # TensorBoard 相关
    tb_log_path = Column(String(500))  # 远程服务器上的日志路径
    tb_local_cache_path = Column(String(500))  # 本地缓存路径（event 文件）
    tb_port = Column(Integer, default=6006)
    
    # 实验结果
    results = Column(Text)
    observations = Column(Text)
    conclusion = Column(Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'description': self.description,
            'purpose': self.purpose,
            'status': self.status,
            'tags': self.tags.split(',') if self.tags else [],
            'command_params_json': self.command_params_json,
            'config_json': self.config_json,
            'output_filename': self.output_filename,
            'algorithm': self.algorithm,
            'environment': self.environment,
            'map': self.map,
            'tb_log_path': self.tb_log_path,
            'tb_local_cache_path': self.tb_local_cache_path,
            'tb_port': self.tb_port,
            'results': self.results,
            'observations': self.observations,
            'conclusion': self.conclusion,
            'groups': [{'id': g.id, 'name': g.name} for g in self.groups]
        }
