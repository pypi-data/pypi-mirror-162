from typing import List, Optional
from ddd_objects.domain.entity import Entity, ExpiredEntity
from .value_obj import (
    ContainerArgs,
    ContainerCommand,
    DNSPolicy,
    DockerImageName,
    EnvVarSourceType,
    HTTPHeader,
    ImagePullPolicy,
    Integer,
    JobStatus,
    LabelDict,
    LabelSelectorOperator,
    MatchLabels,
    NetworkScheme,
    NodeSelectorDict,
    PathMode,
    PayType,
    PodResourceDict,
    Protocol,
    RestartPolicy,
    Value,
    Number,
    BandWidth,
    DNSType,
    GPUType,
    NodeName,
    Subdomain,
    VolumeName,
    VolumeType,
    ZoneID,
    Bool,
    Time,
    Path,
    Port,
    Version,
    Password,
    ServiceType,
    DNSLine,
    SecurityGroupID,
    NodeType,
    KeyType,
    DomainName,
    RegionID,
    RecordID,
    Price,
    Token,
    NodeLabel,
    Output,
    Command,
    Size,
    InstanceID,
    Key,
    Endpoint,
    Name,
    InstanceName,
    Type,
    InstanceTypeStatus,
    Hostname,
    IngressHost,
    InternetPayType,
    ImageID,
    Usage,
    NodeStatus,
    Info,
    Weight,
    ID,
    PodStatus,
    InstanceType,
    DateTime,
    TimeInterval,
    InstanceTypeStatusCategory,
    Data,
    IP,
    Username,
    Status
)

class Condition(Entity):
    def __init__(
        self,
        min_cpu_num: Number,
        max_cpu_num: Number,
        min_memory_size: Size,
        max_memory_size: Size,
        min_gpu_num: Optional[Number] = None,
        max_gpu_num: Optional[Number] = None,
        min_gpu_memory_size: Optional[Size] = None,
        max_gpu_memory_size: Optional[Size] = None
    ):
        self.min_cpu_num=min_cpu_num
        self.max_cpu_num=max_cpu_num
        self.min_memory_size=min_memory_size
        self.max_memory_size=max_memory_size
        self.min_gpu_num=min_gpu_num
        self.max_gpu_num=max_gpu_num
        self.min_gpu_memory_size=min_gpu_memory_size
        self.max_gpu_memory_size=max_gpu_memory_size

class InstanceInfo(ExpiredEntity):
    def __init__(
        self,
        id: ID,
        status: Status,
        security_group_id: List[SecurityGroupID],
        instance_type: InstanceType,
        name: Name,
        hostname: Hostname,
        price: Price,
        image_id: ImageID,
        region_id: RegionID,
        zone_id: ZoneID,
        internet_pay_type: InternetPayType,
        pay_type: PayType,
        create_time: DateTime,
        os_name: Name,
        public_ip: List[IP],
        private_ip: IP,
        bandwidth_in: BandWidth,
        bandwidth_out: BandWidth,
        expired_time: DateTime,
        auto_release_time: DateTime,
        key_name: Name,
        _life_time: Number = Number(5)
    ):
        self.id=id
        self.status=status
        self.security_group_id=security_group_id
        self.instance_type=instance_type
        self.name=name
        self.hostname=hostname
        self.price=price
        self.image_id=image_id
        self.region_id=region_id
        self.zone_id=zone_id
        self.internet_pay_type=internet_pay_type
        self.pay_type=pay_type
        self.create_time=create_time
        self.os_name=os_name
        self.public_ip=public_ip
        self.private_ip=private_ip
        self.bandwidth_in=bandwidth_in
        self.bandwidth_out=bandwidth_out
        self.expired_time=expired_time
        self.auto_release_time=auto_release_time
        self.key_name=key_name
        self._life_time=_life_time
        super().__init__(_life_time)

class InstanceUserSetting(Entity):
    def __init__(
        self,
        name: Name,
        password: Password,
        image_id: ImageID,
        region_id: RegionID,
        exclude_instance_types: List[InstanceType],
        user_data: Optional[Data] = None,
        internet_pay_type: Type = Type('PayByTraffic'),
        amount: Number = Number(1),
        bandwidth_in: BandWidth = BandWidth(200),
        bandwidth_out: BandWidth = BandWidth(1),
        disk_size: Size = Size(20),
        key_name: Name = Name('ansible'),
        inner_connection: Bool = Bool(True)
    ):
        self.name=name
        self.password=password
        self.image_id=image_id
        self.region_id=region_id
        self.exclude_instance_types=exclude_instance_types
        self.user_data=user_data
        self.internet_pay_type=internet_pay_type
        self.amount=amount
        self.bandwidth_in=bandwidth_in
        self.bandwidth_out=bandwidth_out
        self.disk_size=disk_size
        self.key_name=key_name
        self.inner_connection=inner_connection

class CommandSetting(Entity):
    def __init__(
        self,
        command: Command = Command('echo 123'),
        forks: Number = Number(100),
        timeout: Number = Number(30),
        password: Password = None,
        username: Username = Username('root'),
        port: Port = Port(22),
        inner_connection: Bool = Bool(True)
    ):
        self.command=command
        self.forks=forks
        self.timeout=timeout
        self.password=password
        self.username=username
        self.port=port
        self.inner_connection=inner_connection

class CommandResult(Entity):
    def __init__(
        self,
        output: Output,
        instance_id: InstanceID,
        instance_name: InstanceName,
        ip: IP,
        succeed: Bool
    ):
        self.output=output
        self.instance_id=instance_id
        self.instance_name=instance_name
        self.ip=ip
        self.succeed=succeed

class OSSOperationInfo(Entity):
    def __init__(
        self,
        name: Name,
        endpoint: Endpoint,
        bucket_name: Name,
        local_path: Path,
        target_path: Path,
        with_tar: Bool = Bool(False)
    ):
        self.name=name
        self.endpoint=endpoint
        self.bucket_name=bucket_name
        self.local_path=local_path
        self.target_path=target_path
        self.with_tar=with_tar

class NodeUserSetting(Entity):
    def __init__(
        self,
        name: NodeName,
        k3s_token: Optional[Token] = None,
        region_id: RegionID = RegionID('cn-zhangjiakou'),
        disk_size: Size = Size(20),
        bandwidth_in: BandWidth = BandWidth(200),
        bandwidth_out: BandWidth = BandWidth(1),
        image_id: ImageID = ImageID('centos_8_5_x64_20G_alibase_20220303.vhd'),
        node_type: NodeType = NodeType('worker'),
        postfix: Bool = Bool(True),
        diff_instance_type: Bool = Bool(False),
        random_password: Bool = Bool(True),
        internet_pay_type: Type = Type('PayByTraffic'),
        master_ip: Optional[IP] = None,
        inner_connection: Bool = Bool(True),
        amount: Number = Number(1)
    ):
        self.name=name
        self.k3s_token=k3s_token
        self.region_id=region_id
        self.disk_size=disk_size
        self.bandwidth_in=bandwidth_in
        self.bandwidth_out=bandwidth_out
        self.image_id=image_id
        self.node_type=node_type
        self.postfix=postfix
        self.diff_instance_type=diff_instance_type
        self.random_password=random_password
        self.internet_pay_type=internet_pay_type
        self.master_ip=master_ip
        self.inner_connection=inner_connection
        self.amount=amount

class NodeInfo(ExpiredEntity):
    def __init__(
        self,
        node_name: NodeName,
        node_type: NodeType,
        node_status: NodeStatus,
        instance_id: InstanceID,
        instance_type: InstanceType,
        hostname: Hostname,
        price: Price,
        image_id: ImageID,
        region_id: RegionID,
        zone_id: ZoneID,
        internet_pay_type: InternetPayType,
        pay_type: PayType,
        security_group_id: List[SecurityGroupID],
        node_label: NodeLabel,
        cpu_number: Number,
        memory_size: Size,
        gpu_type: GPUType,
        gpu_number: Number,
        instance_type_status: InstanceTypeStatus,
        instance_type_status_category: InstanceTypeStatusCategory,
        instance_name: Name,
        instance_status: Status,
        instance_create_time: DateTime,
        os_name: Name,
        public_ip: List[IP],
        private_ip: IP,
        bandwidth_in: BandWidth,
        bandwidth_out: BandWidth,
        expired_time: DateTime,
        auto_release_time: DateTime,
        key_name: Name,
        run_time: Optional[Time] = None,
        k3s_version: Optional[Version] = None,
        _life_time: Number = Number(5)
    ):
        self.node_name=node_name
        self.node_type=node_type
        self.node_status=node_status
        self.instance_id=instance_id
        self.instance_type=instance_type
        self.hostname=hostname
        self.price=price
        self.image_id=image_id
        self.region_id=region_id
        self.zone_id=zone_id
        self.internet_pay_type=internet_pay_type
        self.pay_type=pay_type
        self.security_group_id=security_group_id
        self.node_label=node_label
        self.cpu_number=cpu_number
        self.memory_size=memory_size
        self.gpu_type=gpu_type
        self.gpu_number=gpu_number
        self.instance_type_status=instance_type_status
        self.instance_type_status_category=instance_type_status_category
        self.instance_name=instance_name
        self.instance_status=instance_status
        self.instance_create_time=instance_create_time
        self.os_name=os_name
        self.public_ip=public_ip
        self.private_ip=private_ip
        self.bandwidth_in=bandwidth_in
        self.bandwidth_out=bandwidth_out
        self.expired_time=expired_time
        self.auto_release_time=auto_release_time
        self.key_name=key_name
        self.run_time=run_time
        self.k3s_version=k3s_version
        self._life_time=_life_time
        super().__init__(_life_time)

class InstanceTypeWithStatus(ExpiredEntity):
    def __init__(
        self,
        region_id: RegionID,
        zone_id: ZoneID,
        instance_type_id: InstanceType,
        cpu_number: Number,
        memory_size: Size,
        gpu_type: GPUType,
        gpu_number: Number,
        status: InstanceTypeStatus,
        status_category: InstanceTypeStatusCategory,
        _life_time: Number = Number(5)
    ):
        self.region_id=region_id
        self.zone_id=zone_id
        self.instance_type_id=instance_type_id
        self.cpu_number=cpu_number
        self.memory_size=memory_size
        self.gpu_type=gpu_type
        self.gpu_number=gpu_number
        self.status=status
        self.status_category=status_category
        self._life_time=_life_time
        super().__init__(_life_time)

class InstanceTypeUserSetting(Entity):
    def __init__(
        self,
        region_id: RegionID,
        zone_id: ZoneID,
        instance_type_id: InstanceType
    ):
        self.region_id=region_id
        self.zone_id=zone_id
        self.instance_type_id=instance_type_id

class InstanceUsageInfo(ExpiredEntity):
    def __init__(
        self,
        instance_id: InstanceID,
        instance_name: InstanceName,
        cpu_number: Number,
        cpu_usage: Usage,
        memory_size: Size,
        memory_usage: Usage,
        flow_in: Size,
        flow_out: Size,
        disk_size: Size,
        disk_usage: Usage,
        io_in: Number,
        io_out: Number,
        _life_time: Number = Number(5)
    ):
        self.instance_id=instance_id
        self.instance_name=instance_name
        self.cpu_number=cpu_number
        self.cpu_usage=cpu_usage
        self.memory_size=memory_size
        self.memory_usage=memory_usage
        self.flow_in=flow_in
        self.flow_out=flow_out
        self.disk_size=disk_size
        self.disk_usage=disk_usage
        self.io_in=io_in
        self.io_out=io_out
        self._life_time=_life_time
        super().__init__(_life_time)

class NodeMeta(ExpiredEntity):
    def __init__(
        self,
        name: NodeName,
        status: NodeStatus,
        run_time: Time,
        k3s_version: Version,
        label: NodeLabel,
        private_ip: IP,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.status=status
        self.run_time=run_time
        self.k3s_version=k3s_version
        self.label=label
        self.private_ip=private_ip
        self._life_time=_life_time
        super().__init__(_life_time)

class Namespace(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        status: Status,
        age: TimeInterval,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.status=status
        self.age=age
        self._life_time=_life_time
        super().__init__(_life_time)

class Secret(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        age: TimeInterval,
        namespace: Name,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.age=age
        self.namespace=namespace
        self._life_time=_life_time
        super().__init__(_life_time)

class ConfigMap(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        age: TimeInterval,
        namespace: Name,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.age=age
        self.namespace=namespace
        self._life_time=_life_time
        super().__init__(_life_time)

class ConfigMapUserSetting(Entity):
    def __init__(
        self,
        name: Name,
        key: Key,
        value: Value,
        key_type: KeyType,
        namespace: Name
    ):
        self.name=name
        self.key=key
        self.value=value
        self.key_type=key_type
        self.namespace=namespace

class SecretUserSetting(Entity):
    def __init__(
        self,
        name: Name,
        key: Key,
        value: Value,
        namespace: Name
    ):
        self.name=name
        self.key=key
        self.value=value
        self.namespace=namespace

class Deployment(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        age: TimeInterval,
        namespace: Name,
        ready_info: Info,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.age=age
        self.namespace=namespace
        self.ready_info=ready_info
        self._life_time=_life_time
        super().__init__(_life_time)

class Pod(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        node_name: NodeName,
        pod_status: PodStatus,
        age: TimeInterval,
        pod_ip: IP,
        namespace: Name,
        restarts: Number,
        readiness_info: Optional[Info],
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.node_name=node_name
        self.pod_status=pod_status
        self.age=age
        self.pod_ip=pod_ip
        self.namespace=namespace
        self.restarts=restarts
        self.readiness_info=readiness_info
        self._life_time=_life_time
        super().__init__(_life_time)

class PodOSSOperationInfo(Entity):
    def __init__(
        self,
        name: Name,
        cluster_name: Name,
        namespace_name: Name,
        pod_name: Name,
        container_name: Name,
        target_dir: Path,
        local_path: Path
    ):
        self.name=name
        self.cluster_name=cluster_name
        self.namespace_name=namespace_name
        self.pod_name=pod_name
        self.container_name=container_name
        self.target_dir=target_dir
        self.local_path=local_path

class ResourceOSSSetting(Entity):
    def __init__(
        self,
        cluster_name: Name,
        target_paths: List[Path]
    ):
        self.cluster_name=cluster_name
        self.target_paths=target_paths

class Ingress(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        host_info: Info,
        address_info: Info,
        port: Number,
        age: DateTime,
        namespace: Name,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.host_info=host_info
        self.address_info=address_info
        self.port=port
        self.age=age
        self.namespace=namespace
        self._life_time=_life_time
        super().__init__(_life_time)
    @property
    def hosts(self):
        return [IngressHost(h) for h in self.host_info.get_value().split(',')]
    
    @property
    def addresses(self):
        return [Value(a) for a in self.address_info.get_value().split(',')]

class DNSRecord(Entity):
    def __init__(
        self,
        domain_name: DomainName,
        subdomain: Subdomain,
        value: Value,
        id: Optional[RecordID] = None,
        weight: Optional[Weight] = None,
        dns_type: DNSType = DNSType('A'),
        ttl: Number = Number(600),
        priority: Optional[Number] = None,
        line: Optional[DNSLine] = None
    ):
        self.domain_name=domain_name
        self.subdomain=subdomain
        self.value=value
        self.id=id
        self.weight=weight
        self.dns_type=dns_type
        self.ttl=ttl
        self.priority=priority
        self.line=line

class Service(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        service_type: ServiceType,
        cluster_ip: IP,
        external_ip: Optional[IP],
        port_info: Info,
        age: DateTime,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.service_type=service_type
        self.cluster_ip=cluster_ip
        self.external_ip=external_ip
        self.port_info=port_info
        self.age=age
        self._life_time=_life_time
        super().__init__(_life_time)

class PodContainer(ExpiredEntity):
    def __init__(
        self,
        pod_name: Name,
        init_container_info: Info,
        container_info: Info,
        _life_time: Number = Number(5)
    ):
        self.pod_name=pod_name
        self.init_container_info=init_container_info
        self.container_info=container_info
        self._life_time=_life_time
        super().__init__(_life_time)

class KeyToPath(Entity):
    def __init__(
        self,
        key: Key,
        path: Path,
        mode: Optional[PathMode] = None
    ):
        self.key=key
        self.path=path
        self.mode=mode

# class PodSecurityContext(Entity):
#     def __init__(
#         self,
#         run_as_user: Optional[Number] = None,
#         run_as_group: Optional[Number] = None,
#         run_as_non_root: Optional[Bool] = None
#     ):
#         self.run_as_user=run_as_user
#         self.run_as_group=run_as_group
#         self.run_as_non_root=run_as_non_root

class EnvVarSource(Entity):
    def __init__(
        self,
        env_var_source_type: EnvVarSourceType,
        key: Key,
        name: Name,
        optional: Optional[Bool] = None
    ):
        self.env_var_source_type=env_var_source_type
        self.key=key
        self.name=name
        self.optional=optional

class EnvVar(Entity):
    def __init__(
        self,
        name: Name,
        value: Optional[Value] = None,
        value_from: Optional[EnvVarSource] = None
    ):
        self.name=name
        self.value=value
        self.value_from=value_from

class VolumeSource(Entity):
    def __init__(
        self,
        name: Name,
        volume_type: VolumeType,
        optional: Optional[Bool] = None,
        default_mode: Optional[PathMode] = None,
        items: Optional[List[KeyToPath]] = None
    ):
        self.name=name
        self.volume_type=volume_type
        self.optional=optional
        self.default_mode=default_mode
        self.items = items

class VolumeSetting(Entity):
    def __init__(
        self,
        volume_name: VolumeName,
        empty_dir: Optional[Bool] = None,
        config_map: Optional[VolumeSource] = None,
        secret: Optional[VolumeSource] = None
    ):
        self.volume_name=volume_name
        self.empty_dir=empty_dir
        self.config_map=config_map
        self.secret=secret

class VolumeMount(Entity):
    def __init__(
        self,
        name: Name,
        mount_path: Path,
        read_only: Optional[Bool] = None,
        sub_path: Optional[Path] = None
    ):
        self.name=name
        self.mount_path=mount_path
        self.read_only=read_only
        self.sub_path=sub_path

class HTTPGetAction(Entity):
    def __init__(
        self,
        port: Port,
        host: Optional[IP] = None,
        path: Optional[Path] = None,
        http_headers: Optional[List[HTTPHeader]] = None,
        scheme: Optional[NetworkScheme] = None
    ):
        self.port=port
        self.host=host
        self.path=path
        self.http_headers=http_headers
        self.scheme=scheme

class GRPCAction(Entity):
    def __init__(
        self,
        port: Port,
        service: Optional[Name] = None
    ):
        self.port=port
        self.service=service

class TCPSocketAction(Entity):
    def __init__(
        self,
        port: Port,
        host: Optional[IP] = None
    ):
        self.port=port
        self.host=host

class ContainerPort(Entity):
    def __init__(
        self,
        port: Port,
        name: Optional[Name] = None,
        protocol: Optional[Protocol] = None,
        host_ip: Optional[IP] = None,
        host_port: Optional[Port] = None
    ):
        self.port=port
        self.name=name
        self.protocol=protocol
        self.host_ip=host_ip
        self.host_port=host_port

class Probe(Entity):
    def __init__(
        self,
        initial_delay_seconds: Number = Number(10),
        period_seconds: Number = Number(10),
        success_threshold: Optional[Number] = None,
        timeout_seconds: Number = Number(1),
        command: Optional[List[ContainerCommand]] = None,
        failure_threshold: Number = Number(3),
        grpc: Optional[GRPCAction] = None,
        http_get: Optional[HTTPGetAction] = None,
        tcp_socket: Optional[TCPSocketAction] = None
    ):
        self.initial_delay_seconds=initial_delay_seconds
        self.period_seconds=period_seconds
        self.success_threshold=success_threshold
        self.timeout_seconds=timeout_seconds
        self.command=command
        self.failure_threshold=failure_threshold
        self.grpc=grpc
        self.http_get=http_get
        self.tcp_socket=tcp_socket

class LabelSelectorRequirement(Entity):
    def __init__(
        self,
        key: Key,
        operator: LabelSelectorOperator,
        values: Optional[List[Value]] = None
    ):
        self.key=key
        self.operator=operator
        self.values=values

class LabelSelector(Entity):
    def __init__(
        self,
        match_expressions: Optional[List[LabelSelectorRequirement]],
        match_labels: Optional[MatchLabels],
    ):
        self.match_expressions = match_expressions
        self.match_labels=match_labels

class SecurityContext(Entity):
    def __init__(
        self,
        privileged: Optional[Bool] = None,
        run_as_user: Optional[Number] = None,
        run_as_non_root: Optional[Bool] = None
    ):
        self.privileged=privileged
        self.run_as_user=run_as_user
        self.run_as_non_root=run_as_non_root

class ContainerSetting(Entity):
    def __init__(
        self,
        container_name: Name,
        container_image: DockerImageName,
        env_vars: Optional[List[EnvVar]]=None,
        command: Optional[ContainerCommand]=None,
        args: Optional[ContainerArgs]=None,
        image_pull_policy: Optional[ImagePullPolicy]=ImagePullPolicy('Always'),
        working_dir: Optional[Path]=None,
        volume_mount: Optional[List[VolumeMount]]=None,
        security_context: Optional[SecurityContext]=None,
        limits: Optional[PodResourceDict]=None,
        requests: Optional[PodResourceDict]=None,
        readiness_probe: Optional[Probe]=None,
        liveness_probe: Optional[Probe]=None,
        ports: Optional[List[ContainerPort]]=None
    ):
        self.container_name = container_name
        self.container_image = container_image
        self.env_vars = env_vars
        self.command = command
        self.args = args
        self.image_pull_policy = image_pull_policy
        self.working_dir = working_dir
        self.volume_mount = volume_mount
        self.security_context = security_context
        self.limits = limits
        self.requests = requests
        self.readiness_probe = readiness_probe
        self.liveness_probe = liveness_probe
        self.ports = ports

class JobSetting(Entity):
    def __init__(
        self,
        job_name: Name,
        namespace_name: Name,
        labels: LabelDict,
        containers: List[ContainerSetting],
        init_containers: Optional[List[ContainerSetting]]=None,
        parallelism: Number = Number(1),
        ttl_seconds_after_finished: Number = Number(600),
        restart_policy: RestartPolicy = RestartPolicy('Never'),
        backoff_limit: Number = Number(2),
        node_name: Optional[Name] = None,
        node_selector: Optional[NodeSelectorDict] = None,
        volumes: Optional[List[VolumeSetting]] = None,
        selector: Optional[LabelSelector] = None,
        dns_policy: Optional[DNSPolicy] = None
    ):
        self.job_name = job_name
        self.namespace_name = namespace_name
        self.labels = labels
        self.containers = containers
        self.init_containers = init_containers
        self.parallelism = parallelism
        self.ttl_seconds_after_finished = ttl_seconds_after_finished
        self.restart_policy = restart_policy
        self.backoff_limit = backoff_limit
        self.node_name = node_name
        self.node_selector = node_selector
        self.volumes = volumes
        self.selector = selector
        self.dns_policy = dns_policy

class Job(ExpiredEntity):
    def __init__(
        self,
        name: Name,
        age: DateTime,
        namespace: Name,
        status: JobStatus,
        parallelism: Number,
        _life_time: Number = Number(5)
    ):
        self.name=name
        self.age=age
        self.namespace=namespace
        self.status=status
        self.parallelism=parallelism
        self._life_time=_life_time
        super().__init__(_life_time)

class PodLogSetting(Entity):
    def __init__(
        self,
        namespace_name: Name,
        pod_name: Name,
        container_name: Optional[Name] = None,
        tail_lines: Integer = Integer(500)
    ):
        self.namespace_name=namespace_name
        self.pod_name=pod_name
        self.container_name=container_name
        self.tail_lines=tail_lines

