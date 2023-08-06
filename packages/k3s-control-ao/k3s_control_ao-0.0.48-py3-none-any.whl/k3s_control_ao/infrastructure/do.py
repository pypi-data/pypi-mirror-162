import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from ddd_objects.infrastructure.do import BaseDO

@dataclass
class ConditionDO(BaseDO):
    min_cpu_num: int
    max_cpu_num: int
    min_memory_size: int
    max_memory_size: int
    min_gpu_num: Optional[int]=None
    max_gpu_num: Optional[int]=None
    min_gpu_memory_size: Optional[int]=None
    max_gpu_memory_size: Optional[int]=None

@dataclass
class NodeUserSettingDO(BaseDO):
    name: str
    k3s_token: Optional[str]=None
    region_id: str='cn-zhangjiakou'
    disk_size: int=20
    bandwidth_in: int=200
    bandwidth_out: int=1
    image_id: str='centos_8_5_x64_20G_alibase_20220303.vhd'
    node_type: str='worker'
    postfix: bool=True
    diff_instance_type: bool=False
    random_password: bool=True
    internet_pay_type: str='PayByTraffic'
    master_ip: Optional[str]=None
    inner_connection: bool=True
    amount: int=1

@dataclass
class NodeInfoDO(BaseDO):
    node_name: str
    node_type: str
    node_status: str
    instance_id: str
    instance_type: str
    hostname: str
    price: float
    image_id: str
    region_id: str
    zone_id: str
    internet_pay_type: str
    pay_type: str
    security_group_id: List[str]
    node_label: str
    cpu_number: int
    memory_size: float
    gpu_type: str
    gpu_number: int
    instance_type_status: str
    instance_type_status_category: str
    instance_name: str
    instance_status: str
    instance_create_time: str
    os_name: str
    public_ip: List[str]
    private_ip: str
    bandwidth_in: str
    bandwidth_out: str
    expired_time: str
    auto_release_time: str
    key_name: str
    run_time: Optional[str]=None
    k3s_version: Optional[str]=None
    _life_time: int=5

@dataclass
class CommandResultDO(BaseDO):
    output: str
    instance_id: str
    instance_name: str
    ip: str
    succeed: bool

@dataclass
class NamespaceDO(BaseDO):
    name: str
    status: str
    age: str
    _life_time: int=5

@dataclass
class SecretDO(BaseDO):
    name: str
    age: str
    namespace: str
    _life_time: int=5

@dataclass
class SecretUserSettingDO(BaseDO):
    name: str
    key: str
    value: str
    namespace: str

@dataclass
class ConfigMapDO(BaseDO):
    name: str
    age: str
    namespace: str
    _life_time: int=5

@dataclass
class ConfigMapUserSettingDO(BaseDO):
    name: str
    key: str
    value: str
    key_type: str
    namespace: str

@dataclass
class ResourceOSSSettingDO(BaseDO):
    cluster_name: str
    target_paths: List[str]

@dataclass
class DeploymentDO(BaseDO):
    name: str
    age: str
    namespace: str
    ready_info: str
    _life_time: int=5

@dataclass
class PodDO(BaseDO):
    name: str
    node_name: str
    pod_status: str
    age: str
    pod_ip: str
    namespace: str
    restarts: str
    readiness_info: Optional[str]
    _life_time: int=5

@dataclass
class PodOSSOperationInfoDO(BaseDO):
    name: str
    cluster_name: str
    namespace_name: str
    pod_name: str
    container_name: str
    target_dir: str
    local_path: str

@dataclass
class NodeMetaDO(BaseDO):
    name: str
    status: str
    run_time: str
    k3s_version: str
    label: str
    private_ip: str
    _life_time: int=5

@dataclass
class IngressDO(BaseDO):
    name: str
    host_info: str
    address_info: str
    port: int
    age: str
    namespace: str
    _life_time: int=5

@dataclass
class InstanceInfoDO(BaseDO):
    id: str
    status: str
    security_group_id: List[str]
    instance_type: str
    name: str
    hostname: str
    price: float
    image_id: str
    region_id: str
    zone_id: str
    internet_pay_type: str
    pay_type: str
    create_time: str
    os_name: str
    public_ip: List[str]
    private_ip: str
    bandwidth_in: str
    bandwidth_out: str
    expired_time: str
    auto_release_time: str
    key_name: str
    _life_time: int=5

@dataclass
class InstanceUserSettingDO(BaseDO):
    name: str
    password: str
    image_id: str
    region_id: str
    exclude_instance_types: List[str]
    user_data: Optional[str]=None
    internet_pay_type: str='PayByTraffic'
    amount: int=1
    bandwidth_in: int=200
    bandwidth_out: int=1
    disk_size: int=20
    key_name: str='ansible'
    inner_connection: bool=True

@dataclass
class CommandSettingDO(BaseDO):
    command: str='echo 123'
    forks: int=100
    timeout: int=30
    password: str=None
    username: str='root'
    port: int=22
    inner_connection: bool=True

@dataclass
class OSSOperationInfoDO(BaseDO):
    name: str
    endpoint: str
    bucket_name: str
    local_path: str
    target_path: str
    with_tar: bool=False

@dataclass
class InstanceTypeWithStatusDO(BaseDO):
    region_id: str
    zone_id: str
    instance_type_id: str
    cpu_number: int
    memory_size: float
    gpu_type: str
    gpu_number: int
    status: str
    status_category: str
    _life_time: int=5

@dataclass
class InstanceTypeUserSettingDO(BaseDO):
    region_id: str
    zone_id: str
    instance_type_id: str

@dataclass
class DNSRecordDO(BaseDO):
    domain_name: str
    subdomain: str
    value: str
    id: Optional[str]=None
    weight: Optional[int]=None
    dns_type: str='A'
    ttl: int=600
    priority: Optional[int]=None
    line: Optional[str]=None

@dataclass
class ServiceDO(BaseDO):
    name: str
    service_type: str
    cluster_ip: str
    external_ip: Optional[str]
    port_info: str
    age: str
    _life_time: int=5

@dataclass
class PodContainerDO(BaseDO):
    pod_name: str
    init_container_info: str
    container_info: str
    _life_time: int=5

@dataclass
class KeyToPathDO(BaseDO):
    key: str
    path: str
    mode: Optional[int]=None

# @dataclass
# class PodSecurityContextDO(BaseDO):
#     run_as_user: Optional[int]=None
#     run_as_group: Optional[int]=None
#     run_as_non_root: Optional[bool]=None

@dataclass
class EnvVarSourceDO(BaseDO):
    env_var_source_type: str
    key: str
    name: str
    optional: Optional[bool]=None

@dataclass
class EnvVarDO(BaseDO):
    name: str
    value_from: Optional[EnvVarSourceDO] = None
    value: Optional[str]=None

@dataclass
class VolumeSourceDO(BaseDO):
    name: str  
    volume_type: str
    default_mode: Optional[int] = None
    items: Optional[List[KeyToPathDO]] = None
    optional: Optional[bool] = None

@dataclass
class VolumeSettingDO(BaseDO):
    volume_name: str
    empty_dir: Optional[bool] = None
    config_map: Optional[VolumeSourceDO] = None
    secret: Optional[VolumeSourceDO] = None

@dataclass
class VolumeMountDO(BaseDO):
    name: str
    mount_path: str
    read_only: Optional[bool]=None
    sub_path: Optional[str]=None

@dataclass
class ContainerPortDO(BaseDO):
    port: int
    name: Optional[str] = None
    protocol: Optional[str] = None
    host_ip: Optional[str] = None
    host_port: Optional[int] = None

@dataclass
class HTTPGetActionDO(BaseDO):
    port: int
    host: Optional[str] = None
    path: Optional[str] = None
    http_headers: Optional[List[Dict]] = None
    scheme: Optional[str] = None

@dataclass
class TCPSocketActionDO(BaseDO):
    port: int
    host: Optional[str] = None

@dataclass
class GRPCActionDO(BaseDO):
    port: int
    service: Optional[str] = None

@dataclass
class ProbeDO(BaseDO):
    initial_delay_seconds: int = 10
    period_seconds: int = 10
    success_threshold: Optional[int] = None
    timeout_seconds: int = 1
    command: Optional[List[str]] = None
    failure_threshold: int = 3
    grpc: Optional[GRPCActionDO] = None
    http_get: Optional[HTTPGetActionDO] = None
    tcp_socket: Optional[TCPSocketActionDO] = None

@dataclass
class LabelSelectorRequirementDO(BaseDO):
    key: str
    operator: str
    values: Optional[List[str]] = None

@dataclass
class LabelSelectorDO(BaseDO):
    match_expressions: Optional[List[LabelSelectorRequirementDO]] = None
    match_labels: Optional[Dict] = None

@dataclass
class SecurityContextDO(BaseDO):
    privileged: Optional[bool]=None
    run_as_user: Optional[int]=None
    run_as_non_root: Optional[bool]=None

@dataclass
class ContainerSettingDO(BaseDO):
    container_name: str
    container_image: str
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    env_vars: Optional[List[EnvVarDO]] = None
    image_pull_policy: Optional[str] = None
    working_dir: Optional[str] = None
    volume_mount: Optional[List[VolumeMountDO]] = None
    security_context: Optional[SecurityContextDO] = None
    limits: Optional[Dict] = None
    requests: Optional[Dict] = None
    readiness_probe: Optional[ProbeDO] = None
    liveness_probe: Optional[ProbeDO] = None
    ports: Optional[List[ContainerPortDO]] = None

@dataclass
class JobSettingDO(BaseDO):
    job_name: str
    namespace_name: str
    labels: Dict
    containers: List[ContainerSettingDO]
    init_containers: Optional[List[ContainerSettingDO]]
    node_name: Optional[str] = None
    node_selector: Optional[Dict] = None
    parallelism: int = 1
    ttl_seconds_after_finished: int = 600
    restart_policy: str = 'Never'
    backoff_limit: int = 2
    volumes: Optional[List[VolumeSettingDO]] = None
    selector: Optional[LabelSelectorDO] = None
    dns_policy: Optional[str] = None

@dataclass
class JobDO(BaseDO):
    name: str
    age: Union[str, datetime.timedelta]
    namespace: str
    status: Dict
    parallelism: int
    _life_time: int=5

@dataclass
class PodLogSettingDO(BaseDO):
    namespace_name: str
    pod_name: str
    container_name: Optional[str]=None
    tail_lines: int=500

