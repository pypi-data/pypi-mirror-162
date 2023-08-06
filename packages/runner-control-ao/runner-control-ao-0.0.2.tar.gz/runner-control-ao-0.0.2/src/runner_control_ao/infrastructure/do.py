import datetime
from typing import List, Optional
from dataclasses import dataclass
from ddd_objects.infrastructure.do import BaseDO

@dataclass
class SecretSettingDO(BaseDO):
    secret_name: str
    secret_key: str
    mount_path: str

@dataclass
class ConfigMapSettingDO(BaseDO):
    config_map_name: str
    config_map_key: str
    mount_path: str

@dataclass
class TaskDetailDO(BaseDO):
    age: int
    pod_name: str
    node_name: str
    status: str
    restart: int=0
    output: Optional[str]=None

@dataclass
class TaskUserRequestDO(BaseDO):
    task_name: str
    region_id: str
    cluster_name: str
    git_url: str
    entry_point: Optional[List[str]]
    args: Optional[List[str]]
    image: str
    min_cpu_num: int
    max_cpu_num: int
    min_memory_size: int
    max_memory_size: int
    min_gpu_num: Optional[int]=None
    max_gpu_num: Optional[int]=None
    min_gpu_memory_size: Optional[int]=None
    max_gpu_memory_size: Optional[int]=None
    working_dir: Optional[str]=None
    ports: Optional[List[int]]=None
    parallelism: int=1
    task_sender: Optional[str]=None
    task_life: Optional[int]=None
    task_env: Optional[dict]=None
    secrets: Optional[List[SecretSettingDO]]=None
    config_maps: Optional[List[ConfigMapSettingDO]]=None
    dns_policy: Optional[str]=None

@dataclass
class TaskDO(BaseDO):
    creation_time: datetime.datetime
    task_user_request: TaskUserRequestDO
    id: str
    task_status: str='Pending'
    task_details: Optional[List[TaskDetailDO]]=None
    _life_time: int=86400