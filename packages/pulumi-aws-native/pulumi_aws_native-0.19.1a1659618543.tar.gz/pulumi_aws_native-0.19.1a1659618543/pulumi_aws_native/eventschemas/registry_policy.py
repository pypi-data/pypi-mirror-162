# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['RegistryPolicyArgs', 'RegistryPolicy']

@pulumi.input_type
class RegistryPolicyArgs:
    def __init__(__self__, *,
                 policy: Any,
                 registry_name: pulumi.Input[str],
                 revision_id: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a RegistryPolicy resource.
        """
        pulumi.set(__self__, "policy", policy)
        pulumi.set(__self__, "registry_name", registry_name)
        if revision_id is not None:
            pulumi.set(__self__, "revision_id", revision_id)

    @property
    @pulumi.getter
    def policy(self) -> Any:
        return pulumi.get(self, "policy")

    @policy.setter
    def policy(self, value: Any):
        pulumi.set(self, "policy", value)

    @property
    @pulumi.getter(name="registryName")
    def registry_name(self) -> pulumi.Input[str]:
        return pulumi.get(self, "registry_name")

    @registry_name.setter
    def registry_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "registry_name", value)

    @property
    @pulumi.getter(name="revisionId")
    def revision_id(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "revision_id")

    @revision_id.setter
    def revision_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "revision_id", value)


class RegistryPolicy(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 policy: Optional[Any] = None,
                 registry_name: Optional[pulumi.Input[str]] = None,
                 revision_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Resource Type definition for AWS::EventSchemas::RegistryPolicy

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: RegistryPolicyArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource Type definition for AWS::EventSchemas::RegistryPolicy

        :param str resource_name: The name of the resource.
        :param RegistryPolicyArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(RegistryPolicyArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 policy: Optional[Any] = None,
                 registry_name: Optional[pulumi.Input[str]] = None,
                 revision_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = RegistryPolicyArgs.__new__(RegistryPolicyArgs)

            if policy is None and not opts.urn:
                raise TypeError("Missing required property 'policy'")
            __props__.__dict__["policy"] = policy
            if registry_name is None and not opts.urn:
                raise TypeError("Missing required property 'registry_name'")
            __props__.__dict__["registry_name"] = registry_name
            __props__.__dict__["revision_id"] = revision_id
        super(RegistryPolicy, __self__).__init__(
            'aws-native:eventschemas:RegistryPolicy',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'RegistryPolicy':
        """
        Get an existing RegistryPolicy resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = RegistryPolicyArgs.__new__(RegistryPolicyArgs)

        __props__.__dict__["policy"] = None
        __props__.__dict__["registry_name"] = None
        __props__.__dict__["revision_id"] = None
        return RegistryPolicy(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def policy(self) -> pulumi.Output[Any]:
        return pulumi.get(self, "policy")

    @property
    @pulumi.getter(name="registryName")
    def registry_name(self) -> pulumi.Output[str]:
        return pulumi.get(self, "registry_name")

    @property
    @pulumi.getter(name="revisionId")
    def revision_id(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "revision_id")

