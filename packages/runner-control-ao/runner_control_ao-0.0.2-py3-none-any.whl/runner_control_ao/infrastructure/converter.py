from typing import List
from ddd_objects.infrastructure.converter import Converter
from ..domain.entity import (
    SecretSetting,
    TaskUserRequest,
    ConfigMapSetting,
    TaskDetail
)
from ..domain.value_obj import (
    RegionID,
    TaskDetailOutput,
    Arg,
    SecretKey,
    PodName,
    GitUrl,
    ConfigMapKey,
    GPUNumber,
    ContainerPort,
    TaskDetailStatus,
    DNSPolicy,
    CPUNumber,
    DockerImageName,
    MountPath,
    ConfigMapName,
    ClusterName,
    Age,
    TaskName,
    EntryPoint,
    SecretName,
    TaskEnvDict,
    NodeName,
    WorkingDir,
    MemorySize,
    TaskSender,
    Number
)
from .do import (
    TaskDetailDO,
    TaskUserRequestDO,
    ConfigMapSettingDO,
    SecretSettingDO
)

class SecretSettingConverter(Converter):
    def to_entity(self, do: SecretSettingDO):
        return SecretSetting(
            secret_name = SecretName(do.secret_name),
            secret_key = SecretKey(do.secret_key),
            mount_path = MountPath(do.mount_path)
        )
    def to_do(self, x: SecretSetting):
        return SecretSettingDO(
            secret_name = None if x.secret_name is None else x.secret_name.get_value(),
            secret_key = None if x.secret_key is None else x.secret_key.get_value(),
            mount_path = None if x.mount_path is None else x.mount_path.get_value()
        )
secret_setting_converter = SecretSettingConverter()

class ConfigMapSettingConverter(Converter):
    def to_entity(self, do: ConfigMapSettingDO):
        return ConfigMapSetting(
            config_map_name = ConfigMapName(do.config_map_name),
            config_map_key = ConfigMapKey(do.config_map_key),
            mount_path = MountPath(do.mount_path)
        )
    def to_do(self, x: ConfigMapSetting):
        return ConfigMapSettingDO(
            config_map_name = None if x.config_map_name is None else x.config_map_name.get_value(),
            config_map_key = None if x.config_map_key is None else x.config_map_key.get_value(),
            mount_path = None if x.mount_path is None else x.mount_path.get_value()
        )
config_map_setting_converter = ConfigMapSettingConverter()

class TaskDetailConverter(Converter):
    def to_entity(self, do: TaskDetailDO):
        return TaskDetail(
            age = Age(do.age),
            pod_name = PodName(do.pod_name),
            node_name = NodeName(do.node_name),
            status = TaskDetailStatus(do.status),
            restart = Number(do.restart),
            output = None if do.output is None else TaskDetailOutput(do.output)
        )
    def to_do(self, x: TaskDetail):
        return TaskDetailDO(
            age = None if x.age is None else x.age.get_value(),
            pod_name = None if x.pod_name is None else x.pod_name.get_value(),
            node_name = None if x.node_name is None else x.node_name.get_value(),
            status = None if x.status is None else x.status.get_value(),
            restart = None if x.restart is None else x.restart.get_value(),
            output = None if x.output is None else x.output.get_value()
        )

class TaskUserRequestConverter(Converter):
    def to_entity(self, do: TaskUserRequestDO):
        return TaskUserRequest(
            task_name = TaskName(do.task_name),
            region_id = RegionID(do.region_id),
            cluster_name = ClusterName(do.cluster_name),
            git_url = GitUrl(do.git_url),
            entry_point = None if do.entry_point is None else EntryPoint(do.entry_point),
            args = None if do.args is None else Arg(do.args),
            image = DockerImageName(do.image),
            min_cpu_num = CPUNumber(do.min_cpu_num),
            max_cpu_num = CPUNumber(do.max_cpu_num),
            min_memory_size = MemorySize(do.min_memory_size),
            max_memory_size = MemorySize(do.max_memory_size),
            min_gpu_num = None if do.min_gpu_num is None else GPUNumber(do.min_gpu_num),
            max_gpu_num = None if do.max_gpu_num is None else GPUNumber(do.max_gpu_num),
            min_gpu_memory_size = None if do.min_gpu_memory_size is None else MemorySize(do.min_gpu_memory_size),
            max_gpu_memory_size = None if do.max_gpu_memory_size is None else MemorySize(do.max_gpu_memory_size),
            working_dir = WorkingDir(do.working_dir),
            ports = [ContainerPort(m) for m in do.ports],
            parallelism = Number(do.parallelism),
            task_sender = None if do.task_sender is None else TaskSender(do.task_sender),
            task_life = None if do.task_life is None else Number(do.task_life),
            task_env = None if do.task_env is None else TaskEnvDict(do.task_env),
            secrets = None if do.secrets is None else [secret_setting_converter.to_entity(m) for m in do.secrets],
            config_maps = None if do.config_maps is None else [config_map_setting_converter.to_entity(m) for m in do.config_maps],
            dns_policy = DNSPolicy(do.dns_policy)
        )
    def to_do(self, x: TaskUserRequest):
        return TaskUserRequestDO(
            task_name = None if x.task_name is None else x.task_name.get_value(),
            region_id = None if x.region_id is None else x.region_id.get_value(),
            cluster_name = None if x.cluster_name is None else x.cluster_name.get_value(),
            git_url = None if x.git_url is None else x.git_url.get_value(),
            entry_point = None if x.entry_point is None else x.entry_point.get_value(),
            args = None if x.args is None else x.args.get_value(),
            image = None if x.image is None else x.image.get_value(),
            min_cpu_num = None if x.min_cpu_num is None else x.min_cpu_num.get_value(),
            max_cpu_num = None if x.max_cpu_num is None else x.max_cpu_num.get_value(),
            min_memory_size = None if x.min_memory_size is None else x.min_memory_size.get_value(),
            max_memory_size = None if x.max_memory_size is None else x.max_memory_size.get_value(),
            min_gpu_num = None if x.min_gpu_num is None else x.min_gpu_num.get_value(),
            max_gpu_num = None if x.max_gpu_num is None else x.max_gpu_num.get_value(),
            min_gpu_memory_size = None if x.min_gpu_memory_size is None else x.min_gpu_memory_size.get_value(),
            max_gpu_memory_size = None if x.max_gpu_memory_size is None else x.max_gpu_memory_size.get_value(),
            working_dir = None if x.working_dir is None else x.working_dir.get_value(),
            ports = None if x.ports is None else [m.get_value() for m in x.ports],
            parallelism = None if x.parallelism is None else x.parallelism.get_value(),
            task_sender = None if x.task_sender is None else x.task_sender.get_value(),
            task_life = None if x.task_life is None else x.task_life.get_value(),
            task_env = None if x.task_env is None else x.task_env.get_value(),
            secrets = None if x.secrets is None else [secret_setting_converter.to_do(m) for m in x.secrets],
            config_maps = None if x.config_maps is None else [config_map_setting_converter.to_do(m) for m in x.config_maps],
            dns_policy = None if x.dns_policy is None else x.dns_policy.get_value()
        )

