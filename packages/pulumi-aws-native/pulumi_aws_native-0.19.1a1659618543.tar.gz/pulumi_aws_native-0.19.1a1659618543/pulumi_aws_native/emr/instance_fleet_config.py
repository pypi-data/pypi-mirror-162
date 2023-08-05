# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs
from ._inputs import *

__all__ = ['InstanceFleetConfigArgs', 'InstanceFleetConfig']

@pulumi.input_type
class InstanceFleetConfigArgs:
    def __init__(__self__, *,
                 cluster_id: pulumi.Input[str],
                 instance_fleet_type: pulumi.Input[str],
                 instance_type_configs: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceFleetConfigInstanceTypeConfigArgs']]]] = None,
                 launch_specifications: Optional[pulumi.Input['InstanceFleetConfigInstanceFleetProvisioningSpecificationsArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 target_on_demand_capacity: Optional[pulumi.Input[int]] = None,
                 target_spot_capacity: Optional[pulumi.Input[int]] = None):
        """
        The set of arguments for constructing a InstanceFleetConfig resource.
        """
        pulumi.set(__self__, "cluster_id", cluster_id)
        pulumi.set(__self__, "instance_fleet_type", instance_fleet_type)
        if instance_type_configs is not None:
            pulumi.set(__self__, "instance_type_configs", instance_type_configs)
        if launch_specifications is not None:
            pulumi.set(__self__, "launch_specifications", launch_specifications)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if target_on_demand_capacity is not None:
            pulumi.set(__self__, "target_on_demand_capacity", target_on_demand_capacity)
        if target_spot_capacity is not None:
            pulumi.set(__self__, "target_spot_capacity", target_spot_capacity)

    @property
    @pulumi.getter(name="clusterId")
    def cluster_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "cluster_id")

    @cluster_id.setter
    def cluster_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "cluster_id", value)

    @property
    @pulumi.getter(name="instanceFleetType")
    def instance_fleet_type(self) -> pulumi.Input[str]:
        return pulumi.get(self, "instance_fleet_type")

    @instance_fleet_type.setter
    def instance_fleet_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "instance_fleet_type", value)

    @property
    @pulumi.getter(name="instanceTypeConfigs")
    def instance_type_configs(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['InstanceFleetConfigInstanceTypeConfigArgs']]]]:
        return pulumi.get(self, "instance_type_configs")

    @instance_type_configs.setter
    def instance_type_configs(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceFleetConfigInstanceTypeConfigArgs']]]]):
        pulumi.set(self, "instance_type_configs", value)

    @property
    @pulumi.getter(name="launchSpecifications")
    def launch_specifications(self) -> Optional[pulumi.Input['InstanceFleetConfigInstanceFleetProvisioningSpecificationsArgs']]:
        return pulumi.get(self, "launch_specifications")

    @launch_specifications.setter
    def launch_specifications(self, value: Optional[pulumi.Input['InstanceFleetConfigInstanceFleetProvisioningSpecificationsArgs']]):
        pulumi.set(self, "launch_specifications", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="targetOnDemandCapacity")
    def target_on_demand_capacity(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "target_on_demand_capacity")

    @target_on_demand_capacity.setter
    def target_on_demand_capacity(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "target_on_demand_capacity", value)

    @property
    @pulumi.getter(name="targetSpotCapacity")
    def target_spot_capacity(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "target_spot_capacity")

    @target_spot_capacity.setter
    def target_spot_capacity(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "target_spot_capacity", value)


warnings.warn("""InstanceFleetConfig is not yet supported by AWS Native, so its creation will currently fail. Please use the classic AWS provider, if possible.""", DeprecationWarning)


class InstanceFleetConfig(pulumi.CustomResource):
    warnings.warn("""InstanceFleetConfig is not yet supported by AWS Native, so its creation will currently fail. Please use the classic AWS provider, if possible.""", DeprecationWarning)

    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 cluster_id: Optional[pulumi.Input[str]] = None,
                 instance_fleet_type: Optional[pulumi.Input[str]] = None,
                 instance_type_configs: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceFleetConfigInstanceTypeConfigArgs']]]]] = None,
                 launch_specifications: Optional[pulumi.Input[pulumi.InputType['InstanceFleetConfigInstanceFleetProvisioningSpecificationsArgs']]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 target_on_demand_capacity: Optional[pulumi.Input[int]] = None,
                 target_spot_capacity: Optional[pulumi.Input[int]] = None,
                 __props__=None):
        """
        Resource Type definition for AWS::EMR::InstanceFleetConfig

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: InstanceFleetConfigArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource Type definition for AWS::EMR::InstanceFleetConfig

        :param str resource_name: The name of the resource.
        :param InstanceFleetConfigArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(InstanceFleetConfigArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 cluster_id: Optional[pulumi.Input[str]] = None,
                 instance_fleet_type: Optional[pulumi.Input[str]] = None,
                 instance_type_configs: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceFleetConfigInstanceTypeConfigArgs']]]]] = None,
                 launch_specifications: Optional[pulumi.Input[pulumi.InputType['InstanceFleetConfigInstanceFleetProvisioningSpecificationsArgs']]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 target_on_demand_capacity: Optional[pulumi.Input[int]] = None,
                 target_spot_capacity: Optional[pulumi.Input[int]] = None,
                 __props__=None):
        pulumi.log.warn("""InstanceFleetConfig is deprecated: InstanceFleetConfig is not yet supported by AWS Native, so its creation will currently fail. Please use the classic AWS provider, if possible.""")
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = InstanceFleetConfigArgs.__new__(InstanceFleetConfigArgs)

            if cluster_id is None and not opts.urn:
                raise TypeError("Missing required property 'cluster_id'")
            __props__.__dict__["cluster_id"] = cluster_id
            if instance_fleet_type is None and not opts.urn:
                raise TypeError("Missing required property 'instance_fleet_type'")
            __props__.__dict__["instance_fleet_type"] = instance_fleet_type
            __props__.__dict__["instance_type_configs"] = instance_type_configs
            __props__.__dict__["launch_specifications"] = launch_specifications
            __props__.__dict__["name"] = name
            __props__.__dict__["target_on_demand_capacity"] = target_on_demand_capacity
            __props__.__dict__["target_spot_capacity"] = target_spot_capacity
        super(InstanceFleetConfig, __self__).__init__(
            'aws-native:emr:InstanceFleetConfig',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'InstanceFleetConfig':
        """
        Get an existing InstanceFleetConfig resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = InstanceFleetConfigArgs.__new__(InstanceFleetConfigArgs)

        __props__.__dict__["cluster_id"] = None
        __props__.__dict__["instance_fleet_type"] = None
        __props__.__dict__["instance_type_configs"] = None
        __props__.__dict__["launch_specifications"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["target_on_demand_capacity"] = None
        __props__.__dict__["target_spot_capacity"] = None
        return InstanceFleetConfig(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="clusterId")
    def cluster_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "cluster_id")

    @property
    @pulumi.getter(name="instanceFleetType")
    def instance_fleet_type(self) -> pulumi.Output[str]:
        return pulumi.get(self, "instance_fleet_type")

    @property
    @pulumi.getter(name="instanceTypeConfigs")
    def instance_type_configs(self) -> pulumi.Output[Optional[Sequence['outputs.InstanceFleetConfigInstanceTypeConfig']]]:
        return pulumi.get(self, "instance_type_configs")

    @property
    @pulumi.getter(name="launchSpecifications")
    def launch_specifications(self) -> pulumi.Output[Optional['outputs.InstanceFleetConfigInstanceFleetProvisioningSpecifications']]:
        return pulumi.get(self, "launch_specifications")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="targetOnDemandCapacity")
    def target_on_demand_capacity(self) -> pulumi.Output[Optional[int]]:
        return pulumi.get(self, "target_on_demand_capacity")

    @property
    @pulumi.getter(name="targetSpotCapacity")
    def target_spot_capacity(self) -> pulumi.Output[Optional[int]]:
        return pulumi.get(self, "target_spot_capacity")

