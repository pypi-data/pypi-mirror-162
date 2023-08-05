# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'AppBlockS3LocationArgs',
    'AppBlockScriptDetailsArgs',
    'AppBlockTagArgs',
    'ApplicationS3LocationArgs',
    'ApplicationTagArgs',
    'DirectoryConfigServiceAccountCredentialsArgs',
    'EntitlementAttributeArgs',
    'FleetComputeCapacityArgs',
    'FleetDomainJoinInfoArgs',
    'FleetS3LocationArgs',
    'FleetTagArgs',
    'FleetVpcConfigArgs',
    'ImageBuilderAccessEndpointArgs',
    'ImageBuilderDomainJoinInfoArgs',
    'ImageBuilderTagArgs',
    'ImageBuilderVpcConfigArgs',
    'StackAccessEndpointArgs',
    'StackApplicationSettingsArgs',
    'StackStorageConnectorArgs',
    'StackStreamingExperienceSettingsArgs',
    'StackTagArgs',
    'StackUserSettingArgs',
]

@pulumi.input_type
class AppBlockS3LocationArgs:
    def __init__(__self__, *,
                 s3_bucket: pulumi.Input[str],
                 s3_key: pulumi.Input[str]):
        pulumi.set(__self__, "s3_bucket", s3_bucket)
        pulumi.set(__self__, "s3_key", s3_key)

    @property
    @pulumi.getter(name="s3Bucket")
    def s3_bucket(self) -> pulumi.Input[str]:
        return pulumi.get(self, "s3_bucket")

    @s3_bucket.setter
    def s3_bucket(self, value: pulumi.Input[str]):
        pulumi.set(self, "s3_bucket", value)

    @property
    @pulumi.getter(name="s3Key")
    def s3_key(self) -> pulumi.Input[str]:
        return pulumi.get(self, "s3_key")

    @s3_key.setter
    def s3_key(self, value: pulumi.Input[str]):
        pulumi.set(self, "s3_key", value)


@pulumi.input_type
class AppBlockScriptDetailsArgs:
    def __init__(__self__, *,
                 executable_path: pulumi.Input[str],
                 script_s3_location: pulumi.Input['AppBlockS3LocationArgs'],
                 timeout_in_seconds: pulumi.Input[int],
                 executable_parameters: Optional[pulumi.Input[str]] = None):
        pulumi.set(__self__, "executable_path", executable_path)
        pulumi.set(__self__, "script_s3_location", script_s3_location)
        pulumi.set(__self__, "timeout_in_seconds", timeout_in_seconds)
        if executable_parameters is not None:
            pulumi.set(__self__, "executable_parameters", executable_parameters)

    @property
    @pulumi.getter(name="executablePath")
    def executable_path(self) -> pulumi.Input[str]:
        return pulumi.get(self, "executable_path")

    @executable_path.setter
    def executable_path(self, value: pulumi.Input[str]):
        pulumi.set(self, "executable_path", value)

    @property
    @pulumi.getter(name="scriptS3Location")
    def script_s3_location(self) -> pulumi.Input['AppBlockS3LocationArgs']:
        return pulumi.get(self, "script_s3_location")

    @script_s3_location.setter
    def script_s3_location(self, value: pulumi.Input['AppBlockS3LocationArgs']):
        pulumi.set(self, "script_s3_location", value)

    @property
    @pulumi.getter(name="timeoutInSeconds")
    def timeout_in_seconds(self) -> pulumi.Input[int]:
        return pulumi.get(self, "timeout_in_seconds")

    @timeout_in_seconds.setter
    def timeout_in_seconds(self, value: pulumi.Input[int]):
        pulumi.set(self, "timeout_in_seconds", value)

    @property
    @pulumi.getter(name="executableParameters")
    def executable_parameters(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "executable_parameters")

    @executable_parameters.setter
    def executable_parameters(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "executable_parameters", value)


@pulumi.input_type
class AppBlockTagArgs:
    def __init__(__self__, *,
                 tag_key: pulumi.Input[str],
                 tag_value: pulumi.Input[str]):
        pulumi.set(__self__, "tag_key", tag_key)
        pulumi.set(__self__, "tag_value", tag_value)

    @property
    @pulumi.getter(name="tagKey")
    def tag_key(self) -> pulumi.Input[str]:
        return pulumi.get(self, "tag_key")

    @tag_key.setter
    def tag_key(self, value: pulumi.Input[str]):
        pulumi.set(self, "tag_key", value)

    @property
    @pulumi.getter(name="tagValue")
    def tag_value(self) -> pulumi.Input[str]:
        return pulumi.get(self, "tag_value")

    @tag_value.setter
    def tag_value(self, value: pulumi.Input[str]):
        pulumi.set(self, "tag_value", value)


@pulumi.input_type
class ApplicationS3LocationArgs:
    def __init__(__self__, *,
                 s3_bucket: pulumi.Input[str],
                 s3_key: pulumi.Input[str]):
        pulumi.set(__self__, "s3_bucket", s3_bucket)
        pulumi.set(__self__, "s3_key", s3_key)

    @property
    @pulumi.getter(name="s3Bucket")
    def s3_bucket(self) -> pulumi.Input[str]:
        return pulumi.get(self, "s3_bucket")

    @s3_bucket.setter
    def s3_bucket(self, value: pulumi.Input[str]):
        pulumi.set(self, "s3_bucket", value)

    @property
    @pulumi.getter(name="s3Key")
    def s3_key(self) -> pulumi.Input[str]:
        return pulumi.get(self, "s3_key")

    @s3_key.setter
    def s3_key(self, value: pulumi.Input[str]):
        pulumi.set(self, "s3_key", value)


@pulumi.input_type
class ApplicationTagArgs:
    def __init__(__self__, *,
                 tag_key: pulumi.Input[str],
                 tag_value: pulumi.Input[str]):
        pulumi.set(__self__, "tag_key", tag_key)
        pulumi.set(__self__, "tag_value", tag_value)

    @property
    @pulumi.getter(name="tagKey")
    def tag_key(self) -> pulumi.Input[str]:
        return pulumi.get(self, "tag_key")

    @tag_key.setter
    def tag_key(self, value: pulumi.Input[str]):
        pulumi.set(self, "tag_key", value)

    @property
    @pulumi.getter(name="tagValue")
    def tag_value(self) -> pulumi.Input[str]:
        return pulumi.get(self, "tag_value")

    @tag_value.setter
    def tag_value(self, value: pulumi.Input[str]):
        pulumi.set(self, "tag_value", value)


@pulumi.input_type
class DirectoryConfigServiceAccountCredentialsArgs:
    def __init__(__self__, *,
                 account_name: pulumi.Input[str],
                 account_password: pulumi.Input[str]):
        pulumi.set(__self__, "account_name", account_name)
        pulumi.set(__self__, "account_password", account_password)

    @property
    @pulumi.getter(name="accountName")
    def account_name(self) -> pulumi.Input[str]:
        return pulumi.get(self, "account_name")

    @account_name.setter
    def account_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "account_name", value)

    @property
    @pulumi.getter(name="accountPassword")
    def account_password(self) -> pulumi.Input[str]:
        return pulumi.get(self, "account_password")

    @account_password.setter
    def account_password(self, value: pulumi.Input[str]):
        pulumi.set(self, "account_password", value)


@pulumi.input_type
class EntitlementAttributeArgs:
    def __init__(__self__, *,
                 name: pulumi.Input[str],
                 value: pulumi.Input[str]):
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def name(self) -> pulumi.Input[str]:
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: pulumi.Input[str]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def value(self) -> pulumi.Input[str]:
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: pulumi.Input[str]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class FleetComputeCapacityArgs:
    def __init__(__self__, *,
                 desired_instances: pulumi.Input[int]):
        pulumi.set(__self__, "desired_instances", desired_instances)

    @property
    @pulumi.getter(name="desiredInstances")
    def desired_instances(self) -> pulumi.Input[int]:
        return pulumi.get(self, "desired_instances")

    @desired_instances.setter
    def desired_instances(self, value: pulumi.Input[int]):
        pulumi.set(self, "desired_instances", value)


@pulumi.input_type
class FleetDomainJoinInfoArgs:
    def __init__(__self__, *,
                 directory_name: Optional[pulumi.Input[str]] = None,
                 organizational_unit_distinguished_name: Optional[pulumi.Input[str]] = None):
        if directory_name is not None:
            pulumi.set(__self__, "directory_name", directory_name)
        if organizational_unit_distinguished_name is not None:
            pulumi.set(__self__, "organizational_unit_distinguished_name", organizational_unit_distinguished_name)

    @property
    @pulumi.getter(name="directoryName")
    def directory_name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "directory_name")

    @directory_name.setter
    def directory_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "directory_name", value)

    @property
    @pulumi.getter(name="organizationalUnitDistinguishedName")
    def organizational_unit_distinguished_name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "organizational_unit_distinguished_name")

    @organizational_unit_distinguished_name.setter
    def organizational_unit_distinguished_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "organizational_unit_distinguished_name", value)


@pulumi.input_type
class FleetS3LocationArgs:
    def __init__(__self__, *,
                 s3_bucket: pulumi.Input[str],
                 s3_key: pulumi.Input[str]):
        pulumi.set(__self__, "s3_bucket", s3_bucket)
        pulumi.set(__self__, "s3_key", s3_key)

    @property
    @pulumi.getter(name="s3Bucket")
    def s3_bucket(self) -> pulumi.Input[str]:
        return pulumi.get(self, "s3_bucket")

    @s3_bucket.setter
    def s3_bucket(self, value: pulumi.Input[str]):
        pulumi.set(self, "s3_bucket", value)

    @property
    @pulumi.getter(name="s3Key")
    def s3_key(self) -> pulumi.Input[str]:
        return pulumi.get(self, "s3_key")

    @s3_key.setter
    def s3_key(self, value: pulumi.Input[str]):
        pulumi.set(self, "s3_key", value)


@pulumi.input_type
class FleetTagArgs:
    def __init__(__self__, *,
                 key: pulumi.Input[str],
                 value: pulumi.Input[str]):
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> pulumi.Input[str]:
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: pulumi.Input[str]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter
    def value(self) -> pulumi.Input[str]:
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: pulumi.Input[str]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class FleetVpcConfigArgs:
    def __init__(__self__, *,
                 security_group_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 subnet_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        if security_group_ids is not None:
            pulumi.set(__self__, "security_group_ids", security_group_ids)
        if subnet_ids is not None:
            pulumi.set(__self__, "subnet_ids", subnet_ids)

    @property
    @pulumi.getter(name="securityGroupIds")
    def security_group_ids(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "security_group_ids")

    @security_group_ids.setter
    def security_group_ids(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "security_group_ids", value)

    @property
    @pulumi.getter(name="subnetIds")
    def subnet_ids(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "subnet_ids")

    @subnet_ids.setter
    def subnet_ids(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "subnet_ids", value)


@pulumi.input_type
class ImageBuilderAccessEndpointArgs:
    def __init__(__self__, *,
                 endpoint_type: pulumi.Input[str],
                 vpce_id: pulumi.Input[str]):
        pulumi.set(__self__, "endpoint_type", endpoint_type)
        pulumi.set(__self__, "vpce_id", vpce_id)

    @property
    @pulumi.getter(name="endpointType")
    def endpoint_type(self) -> pulumi.Input[str]:
        return pulumi.get(self, "endpoint_type")

    @endpoint_type.setter
    def endpoint_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "endpoint_type", value)

    @property
    @pulumi.getter(name="vpceId")
    def vpce_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "vpce_id")

    @vpce_id.setter
    def vpce_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "vpce_id", value)


@pulumi.input_type
class ImageBuilderDomainJoinInfoArgs:
    def __init__(__self__, *,
                 directory_name: Optional[pulumi.Input[str]] = None,
                 organizational_unit_distinguished_name: Optional[pulumi.Input[str]] = None):
        if directory_name is not None:
            pulumi.set(__self__, "directory_name", directory_name)
        if organizational_unit_distinguished_name is not None:
            pulumi.set(__self__, "organizational_unit_distinguished_name", organizational_unit_distinguished_name)

    @property
    @pulumi.getter(name="directoryName")
    def directory_name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "directory_name")

    @directory_name.setter
    def directory_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "directory_name", value)

    @property
    @pulumi.getter(name="organizationalUnitDistinguishedName")
    def organizational_unit_distinguished_name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "organizational_unit_distinguished_name")

    @organizational_unit_distinguished_name.setter
    def organizational_unit_distinguished_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "organizational_unit_distinguished_name", value)


@pulumi.input_type
class ImageBuilderTagArgs:
    def __init__(__self__, *,
                 key: pulumi.Input[str],
                 value: pulumi.Input[str]):
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> pulumi.Input[str]:
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: pulumi.Input[str]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter
    def value(self) -> pulumi.Input[str]:
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: pulumi.Input[str]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class ImageBuilderVpcConfigArgs:
    def __init__(__self__, *,
                 security_group_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 subnet_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        if security_group_ids is not None:
            pulumi.set(__self__, "security_group_ids", security_group_ids)
        if subnet_ids is not None:
            pulumi.set(__self__, "subnet_ids", subnet_ids)

    @property
    @pulumi.getter(name="securityGroupIds")
    def security_group_ids(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "security_group_ids")

    @security_group_ids.setter
    def security_group_ids(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "security_group_ids", value)

    @property
    @pulumi.getter(name="subnetIds")
    def subnet_ids(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "subnet_ids")

    @subnet_ids.setter
    def subnet_ids(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "subnet_ids", value)


@pulumi.input_type
class StackAccessEndpointArgs:
    def __init__(__self__, *,
                 endpoint_type: pulumi.Input[str],
                 vpce_id: pulumi.Input[str]):
        pulumi.set(__self__, "endpoint_type", endpoint_type)
        pulumi.set(__self__, "vpce_id", vpce_id)

    @property
    @pulumi.getter(name="endpointType")
    def endpoint_type(self) -> pulumi.Input[str]:
        return pulumi.get(self, "endpoint_type")

    @endpoint_type.setter
    def endpoint_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "endpoint_type", value)

    @property
    @pulumi.getter(name="vpceId")
    def vpce_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "vpce_id")

    @vpce_id.setter
    def vpce_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "vpce_id", value)


@pulumi.input_type
class StackApplicationSettingsArgs:
    def __init__(__self__, *,
                 enabled: pulumi.Input[bool],
                 settings_group: Optional[pulumi.Input[str]] = None):
        pulumi.set(__self__, "enabled", enabled)
        if settings_group is not None:
            pulumi.set(__self__, "settings_group", settings_group)

    @property
    @pulumi.getter
    def enabled(self) -> pulumi.Input[bool]:
        return pulumi.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: pulumi.Input[bool]):
        pulumi.set(self, "enabled", value)

    @property
    @pulumi.getter(name="settingsGroup")
    def settings_group(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "settings_group")

    @settings_group.setter
    def settings_group(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "settings_group", value)


@pulumi.input_type
class StackStorageConnectorArgs:
    def __init__(__self__, *,
                 connector_type: pulumi.Input[str],
                 domains: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 resource_identifier: Optional[pulumi.Input[str]] = None):
        pulumi.set(__self__, "connector_type", connector_type)
        if domains is not None:
            pulumi.set(__self__, "domains", domains)
        if resource_identifier is not None:
            pulumi.set(__self__, "resource_identifier", resource_identifier)

    @property
    @pulumi.getter(name="connectorType")
    def connector_type(self) -> pulumi.Input[str]:
        return pulumi.get(self, "connector_type")

    @connector_type.setter
    def connector_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "connector_type", value)

    @property
    @pulumi.getter
    def domains(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "domains")

    @domains.setter
    def domains(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "domains", value)

    @property
    @pulumi.getter(name="resourceIdentifier")
    def resource_identifier(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "resource_identifier")

    @resource_identifier.setter
    def resource_identifier(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_identifier", value)


@pulumi.input_type
class StackStreamingExperienceSettingsArgs:
    def __init__(__self__, *,
                 preferred_protocol: Optional[pulumi.Input[str]] = None):
        if preferred_protocol is not None:
            pulumi.set(__self__, "preferred_protocol", preferred_protocol)

    @property
    @pulumi.getter(name="preferredProtocol")
    def preferred_protocol(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "preferred_protocol")

    @preferred_protocol.setter
    def preferred_protocol(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "preferred_protocol", value)


@pulumi.input_type
class StackTagArgs:
    def __init__(__self__, *,
                 key: pulumi.Input[str],
                 value: pulumi.Input[str]):
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> pulumi.Input[str]:
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: pulumi.Input[str]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter
    def value(self) -> pulumi.Input[str]:
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: pulumi.Input[str]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class StackUserSettingArgs:
    def __init__(__self__, *,
                 action: pulumi.Input[str],
                 permission: pulumi.Input[str]):
        pulumi.set(__self__, "action", action)
        pulumi.set(__self__, "permission", permission)

    @property
    @pulumi.getter
    def action(self) -> pulumi.Input[str]:
        return pulumi.get(self, "action")

    @action.setter
    def action(self, value: pulumi.Input[str]):
        pulumi.set(self, "action", value)

    @property
    @pulumi.getter
    def permission(self) -> pulumi.Input[str]:
        return pulumi.get(self, "permission")

    @permission.setter
    def permission(self, value: pulumi.Input[str]):
        pulumi.set(self, "permission", value)


