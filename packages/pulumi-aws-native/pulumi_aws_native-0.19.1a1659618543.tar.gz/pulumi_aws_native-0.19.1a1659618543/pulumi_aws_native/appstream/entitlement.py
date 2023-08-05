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

__all__ = ['EntitlementArgs', 'Entitlement']

@pulumi.input_type
class EntitlementArgs:
    def __init__(__self__, *,
                 app_visibility: pulumi.Input[str],
                 attributes: pulumi.Input[Sequence[pulumi.Input['EntitlementAttributeArgs']]],
                 stack_name: pulumi.Input[str],
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a Entitlement resource.
        """
        pulumi.set(__self__, "app_visibility", app_visibility)
        pulumi.set(__self__, "attributes", attributes)
        pulumi.set(__self__, "stack_name", stack_name)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter(name="appVisibility")
    def app_visibility(self) -> pulumi.Input[str]:
        return pulumi.get(self, "app_visibility")

    @app_visibility.setter
    def app_visibility(self, value: pulumi.Input[str]):
        pulumi.set(self, "app_visibility", value)

    @property
    @pulumi.getter
    def attributes(self) -> pulumi.Input[Sequence[pulumi.Input['EntitlementAttributeArgs']]]:
        return pulumi.get(self, "attributes")

    @attributes.setter
    def attributes(self, value: pulumi.Input[Sequence[pulumi.Input['EntitlementAttributeArgs']]]):
        pulumi.set(self, "attributes", value)

    @property
    @pulumi.getter(name="stackName")
    def stack_name(self) -> pulumi.Input[str]:
        return pulumi.get(self, "stack_name")

    @stack_name.setter
    def stack_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "stack_name", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)


class Entitlement(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 app_visibility: Optional[pulumi.Input[str]] = None,
                 attributes: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['EntitlementAttributeArgs']]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 stack_name: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Resource Type definition for AWS::AppStream::Entitlement

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: EntitlementArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource Type definition for AWS::AppStream::Entitlement

        :param str resource_name: The name of the resource.
        :param EntitlementArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(EntitlementArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 app_visibility: Optional[pulumi.Input[str]] = None,
                 attributes: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['EntitlementAttributeArgs']]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 stack_name: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = EntitlementArgs.__new__(EntitlementArgs)

            if app_visibility is None and not opts.urn:
                raise TypeError("Missing required property 'app_visibility'")
            __props__.__dict__["app_visibility"] = app_visibility
            if attributes is None and not opts.urn:
                raise TypeError("Missing required property 'attributes'")
            __props__.__dict__["attributes"] = attributes
            __props__.__dict__["description"] = description
            __props__.__dict__["name"] = name
            if stack_name is None and not opts.urn:
                raise TypeError("Missing required property 'stack_name'")
            __props__.__dict__["stack_name"] = stack_name
            __props__.__dict__["created_time"] = None
            __props__.__dict__["last_modified_time"] = None
        super(Entitlement, __self__).__init__(
            'aws-native:appstream:Entitlement',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Entitlement':
        """
        Get an existing Entitlement resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = EntitlementArgs.__new__(EntitlementArgs)

        __props__.__dict__["app_visibility"] = None
        __props__.__dict__["attributes"] = None
        __props__.__dict__["created_time"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["last_modified_time"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["stack_name"] = None
        return Entitlement(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="appVisibility")
    def app_visibility(self) -> pulumi.Output[str]:
        return pulumi.get(self, "app_visibility")

    @property
    @pulumi.getter
    def attributes(self) -> pulumi.Output[Sequence['outputs.EntitlementAttribute']]:
        return pulumi.get(self, "attributes")

    @property
    @pulumi.getter(name="createdTime")
    def created_time(self) -> pulumi.Output[str]:
        return pulumi.get(self, "created_time")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="lastModifiedTime")
    def last_modified_time(self) -> pulumi.Output[str]:
        return pulumi.get(self, "last_modified_time")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="stackName")
    def stack_name(self) -> pulumi.Output[str]:
        return pulumi.get(self, "stack_name")

