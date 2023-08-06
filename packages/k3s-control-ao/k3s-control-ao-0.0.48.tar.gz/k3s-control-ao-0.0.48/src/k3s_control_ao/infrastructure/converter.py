from typing import List
from ddd_objects.infrastructure.converter import Converter
from ..domain.entity import (
    ContainerPort,
    ContainerSetting,
    DNSRecord,
    EnvVar,
    EnvVarSource,
    GRPCAction,
    HTTPGetAction,
    Job,
    JobSetting,
    KeyToPath,
    LabelSelector,
    LabelSelectorRequirement,
    NodeInfo,
    NodeUserSetting,
    Pod,
    PodLogSetting,
    Probe,
    SecretUserSetting,
    Namespace,
    ConfigMap,
    Secret,
    OSSOperationInfo,
    Deployment,
    Condition,
    PodContainer,
    InstanceTypeWithStatus,
    InstanceUserSetting,
    ResourceOSSSetting,
    InstanceInfo,
    CommandResult,
    ConfigMapUserSetting,
    NodeMeta,
    CommandSetting,
    SecurityContext,
    Service,
    InstanceTypeUserSetting,
    PodOSSOperationInfo,
    Ingress,
    TCPSocketAction,
    VolumeMount,
    VolumeSetting,
    VolumeSource
)
from ..domain.value_obj import (
    ContainerCommand,
    EnvVarSourceType,
    HTTPHeader,
    Integer,
    JobStatus,
    LabelSelectorOperator,
    MatchLabels,
    NetworkScheme,
    PathMode,
    PayType,
    Protocol,
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
from .do import (
    ContainerPortDO,
    ContainerSettingDO,
    EnvVarDO,
    EnvVarSourceDO,
    GRPCActionDO,
    HTTPGetActionDO,
    InstanceTypeUserSettingDO,
    JobDO,
    JobSettingDO,
    KeyToPathDO,
    LabelSelectorDO,
    LabelSelectorRequirementDO,
    PodLogSettingDO,
    ProbeDO,
    SecretDO,
    NamespaceDO,
    DNSRecordDO,
    NodeUserSettingDO,
    PodContainerDO,
    DeploymentDO,
    CommandResultDO,
    InstanceUserSettingDO,
    ConfigMapUserSettingDO,
    IngressDO,
    ConfigMapDO,
    InstanceInfoDO,
    NodeInfoDO,
    SecurityContextDO,
    ServiceDO,
    SecretUserSettingDO,
    PodDO,
    InstanceTypeWithStatusDO,
    CommandSettingDO,
    PodOSSOperationInfoDO,
    OSSOperationInfoDO,
    NodeMetaDO,
    ResourceOSSSettingDO,
    ConditionDO,
    TCPSocketActionDO,
    VolumeMountDO,
    VolumeSettingDO,
    VolumeSourceDO
)

class ConditionConverter(Converter):
    def to_entity(self, do: ConditionDO):
        return Condition(
            min_cpu_num = Number(do.min_cpu_num),
            max_cpu_num = Number(do.max_cpu_num),
            min_memory_size = Size(do.min_memory_size),
            max_memory_size = Size(do.max_memory_size),
            min_gpu_num = Number(do.min_gpu_num),
            max_gpu_num = Number(do.max_gpu_num),
            min_gpu_memory_size = Size(do.min_gpu_memory_size),
            max_gpu_memory_size = Size(do.max_gpu_memory_size)
        )
    def to_do(self, x: Condition):
        return ConditionDO(
            min_cpu_num = None if x.min_cpu_num is None else x.min_cpu_num.get_value(),
            max_cpu_num = None if x.max_cpu_num is None else x.max_cpu_num.get_value(),
            min_memory_size = None if x.min_memory_size is None else x.min_memory_size.get_value(),
            max_memory_size = None if x.max_memory_size is None else x.max_memory_size.get_value(),
            min_gpu_num = None if x.min_gpu_num is None else x.min_gpu_num.get_value(),
            max_gpu_num = None if x.max_gpu_num is None else x.max_gpu_num.get_value(),
            min_gpu_memory_size = None if x.min_gpu_memory_size is None else x.min_gpu_memory_size.get_value(),
            max_gpu_memory_size = None if x.max_gpu_memory_size is None else x.max_gpu_memory_size.get_value()
        )

class CommandResultConverter(Converter):
    def to_entity(self, do: CommandResultDO):
        return CommandResult(
            output = Output(do.output),
            instance_id = InstanceID(do.instance_id),
            instance_name = InstanceName(do.instance_name),
            ip = IP(do.ip),
            succeed = Bool(do.succeed)
        )
    def to_do(self, x: CommandResult):
        return CommandResultDO(
            output = None if x.output is None else x.output.get_value(),
            instance_id = None if x.instance_id is None else x.instance_id.get_value(),
            instance_name = None if x.instance_name is None else x.instance_name.get_value(),
            ip = None if x.ip is None else x.ip.get_value(),
            succeed = None if x.succeed is None else x.succeed.get_value()
        )

class NodeUserSettingConverter(Converter):
    def to_entity(self, do: NodeUserSettingDO):
        return NodeUserSetting(
            name = NodeName(do.name),
            k3s_token = Token(do.k3s_token),
            region_id = RegionID(do.region_id),
            disk_size = Size(do.disk_size),
            bandwidth_in = BandWidth(do.bandwidth_in),
            bandwidth_out = BandWidth(do.bandwidth_out),
            image_id = ImageID(do.image_id),
            node_type = NodeType(do.node_type),
            postfix = Bool(do.postfix),
            diff_instance_type = Bool(do.diff_instance_type),
            random_password = Bool(do.random_password),
            internet_pay_type = Type(do.internet_pay_type),
            master_ip = IP(do.master_ip),
            inner_connection = Bool(do.inner_connection),
            amount = Number(do.amount)
        )
    def to_do(self, x: NodeUserSetting):
        return NodeUserSettingDO(
            name = None if x.name is None else x.name.get_value(),
            k3s_token = None if x.k3s_token is None else x.k3s_token.get_value(),
            region_id = None if x.region_id is None else x.region_id.get_value(),
            disk_size = None if x.disk_size is None else x.disk_size.get_value(),
            bandwidth_in = None if x.bandwidth_in is None else x.bandwidth_in.get_value(),
            bandwidth_out = None if x.bandwidth_out is None else x.bandwidth_out.get_value(),
            image_id = None if x.image_id is None else x.image_id.get_value(),
            node_type = None if x.node_type is None else x.node_type.get_value(),
            postfix = None if x.postfix is None else x.postfix.get_value(),
            diff_instance_type = None if x.diff_instance_type is None else x.diff_instance_type.get_value(),
            random_password = None if x.random_password is None else x.random_password.get_value(),
            internet_pay_type = None if x.internet_pay_type is None else x.internet_pay_type.get_value(),
            master_ip = None if x.master_ip is None else x.master_ip.get_value(),
            inner_connection = None if x.inner_connection is None else x.inner_connection.get_value(),
            amount = None if x.amount is None else x.amount.get_value()
        )

class NamespaceConverter(Converter):
    def to_entity(self, do: NamespaceDO):
        return Namespace(
            name = Name(do.name),
            status = Status(do.status),
            age = TimeInterval(do.age),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Namespace):
        return NamespaceDO(
            name = None if x.name is None else x.name.get_value(),
            status = None if x.status is None else x.status.get_value(),
            age = None if x.age is None else x.age.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class SecretConverter(Converter):
    def to_entity(self, do: SecretDO):
        return Secret(
            name = Name(do.name),
            age = TimeInterval(do.age),
            namespace = Name(do.namespace),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Secret):
        return SecretDO(
            name = None if x.name is None else x.name.get_value(),
            age = None if x.age is None else x.age.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class ConfigMapConverter(Converter):
    def to_entity(self, do: ConfigMapDO):
        return ConfigMap(
            name = Name(do.name),
            age = TimeInterval(do.age),
            namespace = Name(do.namespace),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: ConfigMap):
        return ConfigMapDO(
            name = None if x.name is None else x.name.get_value(),
            age = None if x.age is None else x.age.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class ConfigMapUserSettingConverter(Converter):
    def to_entity(self, do: ConfigMapUserSettingDO):
        return ConfigMapUserSetting(
            name = Name(do.name),
            key = Key(do.key),
            value = Value(do.value),
            key_type = KeyType(do.key_type),
            namespace = Name(do.namespace)
        )
    def to_do(self, x: ConfigMapUserSetting):
        return ConfigMapUserSettingDO(
            name = None if x.name is None else x.name.get_value(),
            key = None if x.key is None else x.key.get_value(),
            value = None if x.value is None else x.value.get_value(),
            key_type = None if x.key_type is None else x.key_type.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value()
        )

class SecretUserSettingConverter(Converter):
    def to_entity(self, do: SecretUserSettingDO):
        return SecretUserSetting(
            name = Name(do.name),
            key = Key(do.key),
            value = Value(do.value),
            namespace = Name(do.namespace)
        )
    def to_do(self, x: SecretUserSetting):
        return SecretUserSettingDO(
            name = None if x.name is None else x.name.get_value(),
            key = None if x.key is None else x.key.get_value(),
            value = None if x.value is None else x.value.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value()
        )

class DeploymentConverter(Converter):
    def to_entity(self, do: DeploymentDO):
        return Deployment(
            name = Name(do.name),
            age = TimeInterval(do.age),
            namespace = Name(do.namespace),
            ready_info = Info(do.ready_info),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Deployment):
        return DeploymentDO(
            name = None if x.name is None else x.name.get_value(),
            age = None if x.age is None else x.age.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value(),
            ready_info = None if x.ready_info is None else x.ready_info.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class PodConverter(Converter):
    def to_entity(self, do: PodDO):
        return Pod(
            name = Name(do.name),
            node_name = NodeName(do.node_name),
            pod_status = PodStatus(do.pod_status),
            age = TimeInterval(do.age),
            pod_ip = IP(do.pod_ip),
            namespace = Name(do.namespace),
            restarts = Number(do.restarts),
            readiness_info = Info(do.readiness_info),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Pod):
        return PodDO(
            name = None if x.name is None else x.name.get_value(),
            node_name = None if x.node_name is None else x.node_name.get_value(),
            pod_status = None if x.pod_status is None else x.pod_status.get_value(),
            age = None if x.age is None else x.age.get_value(),
            pod_ip = None if x.pod_ip is None else x.pod_ip.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value(),
            restarts = None if x.restarts is None else x.restarts.get_value(),
            readiness_info = None if x.readiness_info is None else x.readiness_info.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class PodOSSOperationInfoConverter(Converter):
    def to_entity(self, do: PodOSSOperationInfoDO):
        return PodOSSOperationInfo(
            name = Name(do.name),
            cluster_name = Name(do.cluster_name),
            namespace_name = Name(do.namespace_name),
            pod_name = Name(do.pod_name),
            container_name = Name(do.container_name),
            target_dir = Path(do.target_dir),
            local_path = Path(do.local_path)
        )
    def to_do(self, x: PodOSSOperationInfo):
        return PodOSSOperationInfoDO(
            name = None if x.name is None else x.name.get_value(),
            cluster_name = None if x.cluster_name is None else x.cluster_name.get_value(),
            namespace_name = None if x.namespace_name is None else x.namespace_name.get_value(),
            pod_name = None if x.pod_name is None else x.pod_name.get_value(),
            container_name = None if x.container_name is None else x.container_name.get_value(),
            target_dir = None if x.target_dir is None else x.target_dir.get_value(),
            local_path = None if x.local_path is None else x.local_path.get_value()
        )

class ResourceOSSSettingConverter(Converter):
    def to_entity(self, do: ResourceOSSSettingDO):
        return ResourceOSSSetting(
            cluster_name = Name(do.cluster_name),
            target_paths = [Path(m) for m in do.target_paths]
        )
    def to_do(self, x: ResourceOSSSetting):
        return ResourceOSSSettingDO(
            cluster_name = None if x.cluster_name is None else x.cluster_name.get_value(),
            target_paths = None if x.target_paths is None else [m.get_value() for m in x.target_paths]
        )

class NodeInfoConverter(Converter):
    def to_entity(self, do: NodeInfoDO):
        return NodeInfo(
            node_name = NodeName(do.node_name),
            node_type = NodeType(do.node_type),
            node_status = NodeStatus(do.node_status),
            instance_id = InstanceID(do.instance_id),
            instance_type = InstanceType(do.instance_type),
            hostname = Hostname(do.hostname),
            price = Price(do.price),
            image_id = ImageID(do.image_id),
            region_id = RegionID(do.region_id),
            zone_id = ZoneID(do.zone_id),
            internet_pay_type = InternetPayType(do.internet_pay_type),
            pay_type = PayType(do.pay_type),
            security_group_id = [SecurityGroupID(m) for m in do.security_group_id],
            node_label = NodeLabel(do.node_label),
            cpu_number = Number(do.cpu_number),
            memory_size = Size(do.memory_size),
            gpu_type = GPUType(do.gpu_type),
            gpu_number = Number(do.gpu_number),
            instance_type_status = InstanceTypeStatus(do.instance_type_status),
            instance_type_status_category = InstanceTypeStatusCategory(do.instance_type_status_category),
            instance_name = Name(do.instance_name),
            instance_status = Status(do.instance_status),
            instance_create_time = DateTime(do.instance_create_time),
            os_name = Name(do.os_name),
            public_ip = [IP(m) for m in do.public_ip],
            private_ip = IP(do.private_ip),
            bandwidth_in = BandWidth(do.bandwidth_in),
            bandwidth_out = BandWidth(do.bandwidth_out),
            expired_time = DateTime(do.expired_time),
            auto_release_time = DateTime(do.auto_release_time),
            key_name = Name(do.key_name),
            run_time = Time(do.run_time),
            k3s_version = Version(do.k3s_version),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: NodeInfo):
        return NodeInfoDO(
            node_name = None if x.node_name is None else x.node_name.get_value(),
            node_type = None if x.node_type is None else x.node_type.get_value(),
            node_status = None if x.node_status is None else x.node_status.get_value(),
            instance_id = None if x.instance_id is None else x.instance_id.get_value(),
            instance_type = None if x.instance_type is None else x.instance_type.get_value(),
            hostname = None if x.hostname is None else x.hostname.get_value(),
            price = None if x.price is None else x.price.get_value(),
            image_id = None if x.image_id is None else x.image_id.get_value(),
            region_id = None if x.region_id is None else x.region_id.get_value(),
            zone_id = None if x.zone_id is None else x.zone_id.get_value(),
            internet_pay_type = None if x.internet_pay_type is None else x.internet_pay_type.get_value(),
            pay_type = None if x.pay_type is None else x.pay_type.get_value(),
            security_group_id = None if x.security_group_id is None else [m.get_value() for m in x.security_group_id],
            node_label = None if x.node_label is None else x.node_label.get_value(),
            cpu_number = None if x.cpu_number is None else x.cpu_number.get_value(),
            memory_size = None if x.memory_size is None else x.memory_size.get_value(),
            gpu_type = None if x.gpu_type is None else x.gpu_type.get_value(),
            gpu_number = None if x.gpu_number is None else x.gpu_number.get_value(),
            instance_type_status = None if x.instance_type_status is None else x.instance_type_status.get_value(),
            instance_type_status_category = None if x.instance_type_status_category is None else x.instance_type_status_category.get_value(),
            instance_name = None if x.instance_name is None else x.instance_name.get_value(),
            instance_status = None if x.instance_status is None else x.instance_status.get_value(),
            instance_create_time = None if x.instance_create_time is None else x.instance_create_time.get_value(),
            os_name = None if x.os_name is None else x.os_name.get_value(),
            public_ip = None if x.public_ip is None else [m.get_value() for m in x.public_ip],
            private_ip = None if x.private_ip is None else x.private_ip.get_value(),
            bandwidth_in = None if x.bandwidth_in is None else x.bandwidth_in.get_value(),
            bandwidth_out = None if x.bandwidth_out is None else x.bandwidth_out.get_value(),
            expired_time = None if x.expired_time is None else x.expired_time.get_value(),
            auto_release_time = None if x.auto_release_time is None else x.auto_release_time.get_value(),
            key_name = None if x.key_name is None else x.key_name.get_value(),
            run_time = None if x.run_time is None else x.run_time.get_value(),
            k3s_version = None if x.k3s_version is None else x.k3s_version.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class NodeMetaConverter(Converter):
    def to_entity(self, do: NodeMetaDO):
        return NodeMeta(
            name = NodeName(do.name),
            status = NodeStatus(do.status),
            run_time = Time(do.run_time),
            k3s_version = Version(do.k3s_version),
            label = NodeLabel(do.label),
            private_ip = IP(do.private_ip),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: NodeMeta):
        return NodeMetaDO(
            name = None if x.name is None else x.name.get_value(),
            status = None if x.status is None else x.status.get_value(),
            run_time = None if x.run_time is None else x.run_time.get_value(),
            k3s_version = None if x.k3s_version is None else x.k3s_version.get_value(),
            label = None if x.label is None else x.label.get_value(),
            private_ip = None if x.private_ip is None else x.private_ip.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class IngressConverter(Converter):
    def to_entity(self, do: IngressDO):
        return Ingress(
            name = Name(do.name),
            host_info = Info(do.host_info),
            address_info = Info(do.address_info),
            port = Number(do.port),
            age = DateTime(do.age),
            namespace = Name(do.namespace),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Ingress):
        return IngressDO(
            name = None if x.name is None else x.name.get_value(),
            host_info = None if x.host_info is None else x.host_info.get_value(),
            address_info = None if x.address_info is None else x.address_info.get_value(),
            port = None if x.port is None else x.port.get_value(),
            age = None if x.age is None else x.age.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class InstanceInfoConverter(Converter):
    def to_entity(self, do: InstanceInfoDO):
        return InstanceInfo(
            id = ID(do.id),
            status = Status(do.status),
            security_group_id = [SecurityGroupID(m) for m in do.security_group_id],
            instance_type = InstanceType(do.instance_type),
            name = Name(do.name),
            hostname = Hostname(do.hostname),
            price = Price(do.price),
            image_id = ImageID(do.image_id),
            region_id = RegionID(do.region_id),
            zone_id = ZoneID(do.zone_id),
            internet_pay_type = InternetPayType(do.internet_pay_type),
            pay_type = PayType(do.pay_type),
            create_time = DateTime(do.create_time),
            os_name = Name(do.os_name),
            public_ip = [IP(m) for m in do.public_ip],
            private_ip = IP(do.private_ip),
            bandwidth_in = BandWidth(do.bandwidth_in),
            bandwidth_out = BandWidth(do.bandwidth_out),
            expired_time = DateTime(do.expired_time),
            auto_release_time = DateTime(do.auto_release_time),
            key_name = Name(do.key_name),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: InstanceInfo):
        return InstanceInfoDO(
            id = None if x.id is None else x.id.get_value(),
            status = None if x.status is None else x.status.get_value(),
            security_group_id = None if x.security_group_id is None else [m.get_value() for m in x.security_group_id],
            instance_type = None if x.instance_type is None else x.instance_type.get_value(),
            name = None if x.name is None else x.name.get_value(),
            hostname = None if x.hostname is None else x.hostname.get_value(),
            price = None if x.price is None else x.price.get_value(),
            image_id = None if x.image_id is None else x.image_id.get_value(),
            region_id = None if x.region_id is None else x.region_id.get_value(),
            zone_id = None if x.zone_id is None else x.zone_id.get_value(),
            internet_pay_type = None if x.internet_pay_type is None else x.internet_pay_type.get_value(),
            pay_type = None if x.pay_type is None else x.pay_type.get_value(),
            create_time = None if x.create_time is None else x.create_time.get_value(),
            os_name = None if x.os_name is None else x.os_name.get_value(),
            public_ip = None if x.public_ip is None else [m.get_value() for m in x.public_ip],
            private_ip = None if x.private_ip is None else x.private_ip.get_value(),
            bandwidth_in = None if x.bandwidth_in is None else x.bandwidth_in.get_value(),
            bandwidth_out = None if x.bandwidth_out is None else x.bandwidth_out.get_value(),
            expired_time = None if x.expired_time is None else x.expired_time.get_value(),
            auto_release_time = None if x.auto_release_time is None else x.auto_release_time.get_value(),
            key_name = None if x.key_name is None else x.key_name.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class InstanceUserSettingConverter(Converter):
    def to_entity(self, do: InstanceUserSettingDO):
        return InstanceUserSetting(
            name = Name(do.name),
            password = Password(do.password),
            image_id = ImageID(do.image_id),
            region_id = RegionID(do.region_id),
            exclude_instance_types = [InstanceType(m) for m in do.exclude_instance_types],
            user_data = Data(do.user_data),
            internet_pay_type = Type(do.internet_pay_type),
            amount = Number(do.amount),
            bandwidth_in = BandWidth(do.bandwidth_in),
            bandwidth_out = BandWidth(do.bandwidth_out),
            disk_size = Size(do.disk_size),
            key_name = Name(do.key_name),
            inner_connection = Bool(do.inner_connection)
        )
    def to_do(self, x: InstanceUserSetting):
        return InstanceUserSettingDO(
            name = None if x.name is None else x.name.get_value(),
            password = None if x.password is None else x.password.get_value(),
            image_id = None if x.image_id is None else x.image_id.get_value(),
            region_id = None if x.region_id is None else x.region_id.get_value(),
            exclude_instance_types = None if x.exclude_instance_types is None else [m.get_value() for m in x.exclude_instance_types],
            user_data = None if x.user_data is None else x.user_data.get_value(),
            internet_pay_type = None if x.internet_pay_type is None else x.internet_pay_type.get_value(),
            amount = None if x.amount is None else x.amount.get_value(),
            bandwidth_in = None if x.bandwidth_in is None else x.bandwidth_in.get_value(),
            bandwidth_out = None if x.bandwidth_out is None else x.bandwidth_out.get_value(),
            disk_size = None if x.disk_size is None else x.disk_size.get_value(),
            key_name = None if x.key_name is None else x.key_name.get_value(),
            inner_connection = None if x.inner_connection is None else x.inner_connection.get_value()
        )

class CommandSettingConverter(Converter):
    def to_entity(self, do: CommandSettingDO):
        return CommandSetting(
            command = Command(do.command),
            forks = Number(do.forks),
            timeout = Number(do.timeout),
            password = Password(do.password),
            username = Username(do.username),
            port = Port(do.port),
            inner_connection = Bool(do.inner_connection)
        )
    def to_do(self, x: CommandSetting):
        return CommandSettingDO(
            command = None if x.command is None else x.command.get_value(),
            forks = None if x.forks is None else x.forks.get_value(),
            timeout = None if x.timeout is None else x.timeout.get_value(),
            password = None if x.password is None else x.password.get_value(),
            username = None if x.username is None else x.username.get_value(),
            port = None if x.port is None else x.port.get_value(),
            inner_connection = None if x.inner_connection is None else x.inner_connection.get_value()
        )

class OSSOperationInfoConverter(Converter):
    def to_entity(self, do: OSSOperationInfoDO):
        return OSSOperationInfo(
            name = Name(do.name),
            endpoint = Endpoint(do.endpoint),
            bucket_name = Name(do.bucket_name),
            local_path = Path(do.local_path),
            target_path = Path(do.target_path),
            with_tar = Bool(do.with_tar)
        )
    def to_do(self, x: OSSOperationInfo):
        return OSSOperationInfoDO(
            name = None if x.name is None else x.name.get_value(),
            endpoint = None if x.endpoint is None else x.endpoint.get_value(),
            bucket_name = None if x.bucket_name is None else x.bucket_name.get_value(),
            local_path = None if x.local_path is None else x.local_path.get_value(),
            target_path = None if x.target_path is None else x.target_path.get_value(),
            with_tar = None if x.with_tar is None else x.with_tar.get_value()
        )

class InstanceTypeWithStatusConverter(Converter):
    def to_entity(self, do: InstanceTypeWithStatusDO):
        return InstanceTypeWithStatus(
            region_id = RegionID(do.region_id),
            zone_id = ZoneID(do.zone_id),
            instance_type_id = InstanceType(do.instance_type_id),
            cpu_number = Number(do.cpu_number),
            memory_size = Size(do.memory_size),
            gpu_type = GPUType(do.gpu_type),
            gpu_number = Number(do.gpu_number),
            status = InstanceTypeStatus(do.status),
            status_category = InstanceTypeStatusCategory(do.status_category),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: InstanceTypeWithStatus):
        return InstanceTypeWithStatusDO(
            region_id = None if x.region_id is None else x.region_id.get_value(),
            zone_id = None if x.zone_id is None else x.zone_id.get_value(),
            instance_type_id = None if x.instance_type_id is None else x.instance_type_id.get_value(),
            cpu_number = None if x.cpu_number is None else x.cpu_number.get_value(),
            memory_size = None if x.memory_size is None else x.memory_size.get_value(),
            gpu_type = None if x.gpu_type is None else x.gpu_type.get_value(),
            gpu_number = None if x.gpu_number is None else x.gpu_number.get_value(),
            status = None if x.status is None else x.status.get_value(),
            status_category = None if x.status_category is None else x.status_category.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class InstanceTypeUserSettingConverter(Converter):
    def to_entity(self, do: InstanceTypeUserSettingDO):
        return InstanceTypeUserSetting(
            region_id = RegionID(do.region_id),
            zone_id = ZoneID(do.zone_id),
            instance_type_id = InstanceType(do.instance_type_id)
        )
    def to_do(self, x: InstanceTypeUserSetting):
        return InstanceTypeUserSettingDO(
            region_id = None if x.region_id is None else x.region_id.get_value(),
            zone_id = None if x.zone_id is None else x.zone_id.get_value(),
            instance_type_id = None if x.instance_type_id is None else x.instance_type_id.get_value()
        )

class DNSRecordConverter(Converter):
    def to_entity(self, do: DNSRecordDO):
        return DNSRecord(
            domain_name = DomainName(do.domain_name),
            subdomain = Subdomain(do.subdomain),
            value = Value(do.value),
            id = RecordID(do.id),
            weight = Weight(do.weight),
            dns_type = DNSType(do.dns_type),
            ttl = Number(do.ttl),
            priority = Number(do.priority),
            line = DNSLine(do.line)
        )
    def to_do(self, x: DNSRecord):
        return DNSRecordDO(
            domain_name = None if x.domain_name is None else x.domain_name.get_value(),
            subdomain = None if x.subdomain is None else x.subdomain.get_value(),
            value = None if x.value is None else x.value.get_value(),
            id = None if x.id is None else x.id.get_value(),
            weight = None if x.weight is None else x.weight.get_value(),
            dns_type = None if x.dns_type is None else x.dns_type.get_value(),
            ttl = None if x.ttl is None else x.ttl.get_value(),
            priority = None if x.priority is None else x.priority.get_value(),
            line = None if x.line is None else x.line.get_value()
        )

class ServiceConverter(Converter):
    def to_entity(self, do: ServiceDO):
        return Service(
            name = Name(do.name),
            service_type = ServiceType(do.service_type),
            cluster_ip = IP(do.cluster_ip),
            external_ip = IP(do.external_ip),
            port_info = Info(do.port_info),
            age = DateTime(do.age),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Service):
        return ServiceDO(
            name = None if x.name is None else x.name.get_value(),
            service_type = None if x.service_type is None else x.service_type.get_value(),
            cluster_ip = None if x.cluster_ip is None else x.cluster_ip.get_value(),
            external_ip = None if x.external_ip is None else x.external_ip.get_value(),
            port_info = None if x.port_info is None else x.port_info.get_value(),
            age = None if x.age is None else x.age.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class PodContainerConverter(Converter):
    def to_entity(self, do: PodContainerDO):
        return PodContainer(
            pod_name = Name(do.pod_name),
            init_container_info = Info(do.init_container_info),
            container_info = Info(do.container_info),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: PodContainer):
        return PodContainerDO(
            pod_name = None if x.pod_name is None else x.pod_name.get_value(),
            init_container_info = None if x.init_container_info is None else x.init_container_info.get_value(),
            container_info = None if x.container_info is None else x.container_info.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class KeyToPathConverter(Converter):
    def to_entity(self, do: KeyToPathDO):
        return KeyToPath(
            key = Key(do.key),
            path = Path(do.path),
            mode = PathMode(do.mode)
        )
    def to_do(self, x: KeyToPath):
        return KeyToPathDO(
            key = None if x.key is None else x.key.get_value(),
            path = None if x.path is None else x.path.get_value(),
            mode = None if x.mode is None else x.mode.get_value()
        )
key_to_path_converter = KeyToPathConverter()

# class PodSecurityContextConverter(Converter):
#     def to_entity(self, do: PodSecurityContextDO):
#         return PodSecurityContext(
#             run_as_user = Number(do.run_as_user),
#             run_as_group = Number(do.run_as_group),
#             run_as_non_root = Bool(do.run_as_non_root)
#         )
#     def to_do(self, x: PodSecurityContext):
#         return PodSecurityContextDO(
#             run_as_user = None if x.run_as_user is None else x.run_as_user.get_value(),
#             run_as_group = None if x.run_as_group is None else x.run_as_group.get_value(),
#             run_as_non_root = None if x.run_as_non_root is None else x.run_as_non_root.get_value()
#         )
# pod_security_context_converter = PodSecurityContextConverter()

class EnvVarSourceConverter(Converter):
    def to_entity(self, do: EnvVarSourceDO):
        return EnvVarSource(
            env_var_source_type = EnvVarSourceType(do.env_var_source_type),
            key = Key(do.key),
            name = Name(do.name),
            optional = Bool(do.optional)
        )
    def to_do(self, x: EnvVarSource):
        return EnvVarSourceDO(
            env_var_source_type = None if x.env_var_source_type is None else x.env_var_source_type.get_value(),
            key = None if x.key is None else x.key.get_value(),
            name = None if x.name is None else x.name.get_value(),
            optional = None if x.optional is None else x.optional.get_value()
        )
env_var_source_converter = EnvVarSourceConverter()

class EnvVarConverter(Converter):
    def to_entity(self, do: EnvVarDO):
        return EnvVar(
            name = Name(do.name),
            value = Value(do.value),
            value_from = None if do.value_from is None else env_var_source_converter.to_entity(do.value_from)
        )
    def to_do(self, x: EnvVar):
        return EnvVarDO(
            name = None if x.name is None else x.name.get_value(),
            value = None if x.value is None else x.value.get_value(),
            value_from = None if x.value_from is None else env_var_source_converter.to_do(x.value_from)
        )
env_var_converter = EnvVarConverter()

class VolumeSourceConverter(Converter):
    def to_entity(self, do: VolumeSourceDO):
        return VolumeSource(
            name = Name(do.name),
            volume_type = VolumeType(do.volume_type),
            optional = Bool(do.optional),
            default_mode = PathMode(do.default_mode),
            items = None if do.items is None else [key_to_path_converter.to_entity(i) for i in do.items]
        )
    def to_do(self, x: VolumeSource):
        return VolumeSourceDO(
            name = None if x.name is None else x.name.get_value(),
            volume_type = None if x.volume_type is None else x.volume_type.get_value(),
            optional = None if x.optional is None else x.optional.get_value(),
            default_mode = None if x.default_mode is None else x.default_mode.get_value(),
            items = None if x.items is None else [key_to_path_converter.to_do(i) for i in x.items]
        )
volume_source_converter = VolumeSourceConverter()

class VolumeSettingConverter(Converter):
    def to_entity(self, do: VolumeSettingDO):
        return VolumeSetting(
            volume_name = VolumeName(do.volume_name),
            empty_dir = Bool(do.empty_dir),
            config_map= None if do.config_map is None else volume_source_converter.to_entity(do.config_map),
            secret = None if do.secret is None else volume_source_converter.to_entity(do.secret)
        )
    def to_do(self, x: VolumeSetting):
        return VolumeSettingDO(
            volume_name = None if x.volume_name is None else x.volume_name.get_value(),
            empty_dir = None if x.empty_dir is None else x.empty_dir.get_value(),
            config_map = None if x.config_map is None else volume_source_converter.to_do(x.config_map),
            secret = None if x.secret is None else volume_source_converter.to_do(x.secret)
        )
volume_setting_converter = VolumeSettingConverter()

class VolumeMountConverter(Converter):
    def to_entity(self, do: VolumeMountDO):
        return VolumeMount(
            name = Name(do.name),
            mount_path = Path(do.mount_path),
            read_only = Bool(do.read_only),
            sub_path = Path(do.sub_path)
        )
    def to_do(self, x: VolumeMount):
        return VolumeMountDO(
            name = None if x.name is None else x.name.get_value(),
            mount_path = None if x.mount_path is None else x.mount_path.get_value(),
            read_only = None if x.read_only is None else x.read_only.get_value(),
            sub_path = None if x.sub_path is None else x.sub_path.get_value()
        )
volume_mount_converter = VolumeMountConverter()

class HTTPGetActionConverter(Converter):
    def to_entity(self, do: HTTPGetActionDO):
        return HTTPGetAction(
            port = Port(do.port),
            host = IP(do.host),
            path = Path(do.path),
            http_headers = [HTTPHeader(m) for m in do.http_headers],
            scheme = NetworkScheme(do.scheme)
        )
    def to_do(self, x: HTTPGetAction):
        return HTTPGetActionDO(
            port = None if x.port is None else x.port.get_value(),
            host = None if x.host is None else x.host.get_value(),
            path = None if x.path is None else x.path.get_value(),
            http_headers = None if x.http_headers is None else [m.get_value() for m in x.http_headers],
            scheme = None if x.scheme is None else x.scheme.get_value()
        )
http_get_action_converter = HTTPGetActionConverter()

class GRPCActionConverter(Converter):
    def to_entity(self, do: GRPCActionDO):
        return GRPCAction(
            port = Port(do.port),
            service = Name(do.service)
        )
    def to_do(self, x: GRPCAction):
        return GRPCActionDO(
            port = None if x.port is None else x.port.get_value(),
            service = None if x.service is None else x.service.get_value()
        )
grpc_action_converter = GRPCActionConverter()

class TCPSocketActionConverter(Converter):
    def to_entity(self, do: TCPSocketActionDO):
        return TCPSocketAction(
            port = Port(do.port),
            host = IP(do.host)
        )
    def to_do(self, x: TCPSocketAction):
        return TCPSocketActionDO(
            port = None if x.port is None else x.port.get_value(),
            host = None if x.host is None else x.host.get_value()
        )
tcp_socket_action_converter = TCPSocketActionConverter()

class ContainerPortConverter(Converter):
    def to_entity(self, do: ContainerPortDO):
        return ContainerPort(
            port = Port(do.port),
            name = Name(do.name),
            protocol = Protocol(do.protocol),
            host_ip = IP(do.host_ip),
            host_port = Port(do.host_port)
        )
    def to_do(self, x: ContainerPort):
        return ContainerPortDO(
            port = None if x.port is None else x.port.get_value(),
            name = None if x.name is None else x.name.get_value(),
            protocol = None if x.protocol is None else x.protocol.get_value(),
            host_ip = None if x.host_ip is None else x.host_ip.get_value(),
            host_port = None if x.host_port is None else x.host_port.get_value()
        )
container_port_converter = ContainerPortConverter()

class ProbeConverter(Converter):
    def to_entity(self, do: ProbeDO):
        return Probe(
            initial_delay_seconds = Number(do.initial_delay_seconds),
            period_seconds = Number(do.period_seconds),
            success_threshold = Number(do.success_threshold),
            timeout_seconds = Number(do.timeout_seconds),
            command = [ContainerCommand(m) for m in do.command],
            failure_threshold = Number(do.failure_threshold),
            grpc = None if do.grpc is None else grpc_action_converter.to_entity(do.grpc),
            http_get = None if do.http_get is None else http_get_action_converter.to_entity(do.http_get),
            tcp_socket = None if do.tcp_socket is None else tcp_socket_action_converter.to_entity(do.tcp_socket)
        )
    def to_do(self, x: Probe):
        return ProbeDO(
            initial_delay_seconds = None if x.initial_delay_seconds is None else x.initial_delay_seconds.get_value(),
            period_seconds = None if x.period_seconds is None else x.period_seconds.get_value(),
            success_threshold = None if x.success_threshold is None else x.success_threshold.get_value(),
            timeout_seconds = None if x.timeout_seconds is None else x.timeout_seconds.get_value(),
            command = None if x.command is None else [m.get_value() for m in x.command],
            failure_threshold = None if x.failure_threshold is None else x.failure_threshold.get_value(),
            grpc = None if x.grpc is None else grpc_action_converter.to_do(x.grpc),
            http_get = None if x.http_get is None else http_get_action_converter.to_do(x.http_get),
            tcp_socket = None if x.tcp_socket is None else tcp_socket_action_converter.to_do(x.tcp_socket)
        )
probe_converter = ProbeConverter()

class LabelSelectorRequirementConverter(Converter):
    def to_entity(self, do: LabelSelectorRequirementDO):
        return LabelSelectorRequirement(
            key = Key(do.key),
            operator = LabelSelectorOperator(do.operator),
            values = [Value(m) for m in do.values]
        )
    def to_do(self, x: LabelSelectorRequirement):
        return LabelSelectorRequirementDO(
            key = None if x.key is None else x.key.get_value(),
            operator = None if x.operator is None else x.operator.get_value(),
            values = None if x.values is None else [m.get_value() for m in x.values]
        )
label_selector_requirement_converter = LabelSelectorRequirementConverter()

class LabelSelectorConverter(Converter):
    def to_entity(self, do: LabelSelectorDO):
        return LabelSelector(
            match_labels = MatchLabels(do.match_labels),
            match_expressions= None if do.match_expressions is None else [label_selector_requirement_converter.to_entity(i) for i in do.match_expressions]
        )
    def to_do(self, x: LabelSelector):
        return LabelSelectorDO(
            match_labels = None if x.match_labels is None else x.match_labels.get_value(),
            match_expressions = None if x.match_expressions is None else [label_selector_requirement_converter.to_do(i) for i in x.match_expressions]
        )
label_selector_converter =LabelSelectorConverter()

class SecurityContextConverter(Converter):
    def to_entity(self, do: SecurityContextDO):
        return SecurityContext(
            privileged = Bool(do.privileged),
            run_as_user = Number(do.run_as_user),
            run_as_non_root = Bool(do.run_as_non_root)
        )
    def to_do(self, x: SecurityContext):
        return SecurityContextDO(
            privileged = None if x.privileged is None else x.privileged.get_value(),
            run_as_user = None if x.run_as_user is None else x.run_as_user.get_value(),
            run_as_non_root = None if x.run_as_non_root is None else x.run_as_non_root.get_value()
        )
security_context_converter = SecurityContextConverter()

class ContainerSettingConverter(Converter):
    def to_do(self, x: ContainerSetting):
        return ContainerSettingDO(
            container_name = x.container_name.get_value(),
            container_image = x.container_image.get_value(),
            env_vars = None if x.env_vars is None else [env_var_converter.to_do(i) for i in x.env_vars],
            command = None if x.command is None else x.command.get_value(),
            args = None if x.args is None else x.args.get_value(),
            image_pull_policy = None if x.image_pull_policy is None else x.image_pull_policy.get_value(),
            working_dir = None if x.working_dir is None else x.working_dir.get_value(),
            volume_mount = None if x.volume_mount is None else [volume_mount_converter.to_do(i) for i in x.volume_mount],
            security_context = None if x.security_context is None else security_context_converter.to_do(x.security_context),
            limits = None if x.limits is None else x.limits.get_value(),
            requests = None if x.requests is None else x.requests.get_value(),
            readiness_probe = None if x.readiness_probe is None else probe_converter.to_do(x.readiness_probe),
            liveness_probe = None if x.liveness_probe is None else probe_converter.to_do(x.liveness_probe),
            ports = None if x.ports is None else [container_port_converter.to_do(i) for i in x.ports]
        )
container_setting_converter = ContainerSettingConverter()

class JobSettingConverter(Converter):
    def to_do(self, x: JobSetting):
        return JobSettingDO(
            job_name = x.job_name.get_value(),
            namespace_name = x.namespace_name.get_value(),
            labels = x.labels.get_value(),
            containers = [container_setting_converter.to_do(c) for c in x.containers],
            init_containers = None if x.init_containers is None else [container_setting_converter.to_do(i) for i in x.init_containers],
            parallelism = x.parallelism.get_value(),
            ttl_seconds_after_finished = x.ttl_seconds_after_finished.get_value(),
            restart_policy = x.restart_policy.get_value(),
            backoff_limit=x.backoff_limit.get_value(),
            node_name = None if x.node_name is None else x.node_name.get_value(),
            node_selector = None if x.node_selector is None else x.node_selector.get_value(),
            volumes = None if x.volumes is None else [volume_setting_converter.to_do(i) for i in x.volumes],
            selector = None if x.selector is None else [label_selector_converter.to_do(i) for i in x.selector],
            dns_policy = None if x.dns_policy is None else x.dns_policy.get_value()
        )

class JobConverter(Converter):
    def to_entity(self, do: JobDO):
        return Job(
            name = Name(do.name),
            age = DateTime(do.age),
            namespace = Name(do.namespace),
            status = JobStatus(do.status),
            parallelism = Number(do.parallelism),
            _life_time = Number(do._life_time)
        )
    def to_do(self, x: Job):
        return JobDO(
            name = None if x.name is None else x.name.get_value(),
            age = None if x.age is None else x.age.get_value(),
            namespace = None if x.namespace is None else x.namespace.get_value(),
            status = None if x.status is None else x.status.get_value(),
            parallelism = None if x.parallelism is None else x.parallelism.get_value(),
            _life_time = None if x._life_time is None else x._life_time.get_value()
        )

class PodLogSettingConverter(Converter):
    def to_entity(self, do: PodLogSettingDO):
        return PodLogSetting(
            namespace_name = Name(do.namespace_name),
            pod_name = Name(do.pod_name),
            container_name = None if do.container_name is None else Name(do.container_name),
            tail_lines = Integer(do.tail_lines)
        )
    def to_do(self, x: PodLogSetting):
        return PodLogSettingDO(
            namespace_name = None if x.namespace_name is None else x.namespace_name.get_value(),
            pod_name = None if x.pod_name is None else x.pod_name.get_value(),
            container_name = None if x.container_name is None else x.container_name.get_value(),
            tail_lines = None if x.tail_lines is None else x.tail_lines.get_value()
        )

