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

__all__ = ['TransitGatewayConnectArgs', 'TransitGatewayConnect']

@pulumi.input_type
class TransitGatewayConnectArgs:
    def __init__(__self__, *,
                 options: pulumi.Input['TransitGatewayConnectOptionsArgs'],
                 transport_transit_gateway_attachment_id: pulumi.Input[str],
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input['TransitGatewayConnectTagArgs']]]] = None):
        """
        The set of arguments for constructing a TransitGatewayConnect resource.
        :param pulumi.Input['TransitGatewayConnectOptionsArgs'] options: The Connect attachment options.
        :param pulumi.Input[str] transport_transit_gateway_attachment_id: The ID of the attachment from which the Connect attachment was created.
        :param pulumi.Input[Sequence[pulumi.Input['TransitGatewayConnectTagArgs']]] tags: The tags for the attachment.
        """
        pulumi.set(__self__, "options", options)
        pulumi.set(__self__, "transport_transit_gateway_attachment_id", transport_transit_gateway_attachment_id)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter
    def options(self) -> pulumi.Input['TransitGatewayConnectOptionsArgs']:
        """
        The Connect attachment options.
        """
        return pulumi.get(self, "options")

    @options.setter
    def options(self, value: pulumi.Input['TransitGatewayConnectOptionsArgs']):
        pulumi.set(self, "options", value)

    @property
    @pulumi.getter(name="transportTransitGatewayAttachmentId")
    def transport_transit_gateway_attachment_id(self) -> pulumi.Input[str]:
        """
        The ID of the attachment from which the Connect attachment was created.
        """
        return pulumi.get(self, "transport_transit_gateway_attachment_id")

    @transport_transit_gateway_attachment_id.setter
    def transport_transit_gateway_attachment_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "transport_transit_gateway_attachment_id", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['TransitGatewayConnectTagArgs']]]]:
        """
        The tags for the attachment.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['TransitGatewayConnectTagArgs']]]]):
        pulumi.set(self, "tags", value)


class TransitGatewayConnect(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 options: Optional[pulumi.Input[pulumi.InputType['TransitGatewayConnectOptionsArgs']]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['TransitGatewayConnectTagArgs']]]]] = None,
                 transport_transit_gateway_attachment_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        The AWS::EC2::TransitGatewayConnect type

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['TransitGatewayConnectOptionsArgs']] options: The Connect attachment options.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['TransitGatewayConnectTagArgs']]]] tags: The tags for the attachment.
        :param pulumi.Input[str] transport_transit_gateway_attachment_id: The ID of the attachment from which the Connect attachment was created.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: TransitGatewayConnectArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        The AWS::EC2::TransitGatewayConnect type

        :param str resource_name: The name of the resource.
        :param TransitGatewayConnectArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(TransitGatewayConnectArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 options: Optional[pulumi.Input[pulumi.InputType['TransitGatewayConnectOptionsArgs']]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['TransitGatewayConnectTagArgs']]]]] = None,
                 transport_transit_gateway_attachment_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = TransitGatewayConnectArgs.__new__(TransitGatewayConnectArgs)

            if options is None and not opts.urn:
                raise TypeError("Missing required property 'options'")
            __props__.__dict__["options"] = options
            __props__.__dict__["tags"] = tags
            if transport_transit_gateway_attachment_id is None and not opts.urn:
                raise TypeError("Missing required property 'transport_transit_gateway_attachment_id'")
            __props__.__dict__["transport_transit_gateway_attachment_id"] = transport_transit_gateway_attachment_id
            __props__.__dict__["creation_time"] = None
            __props__.__dict__["state"] = None
            __props__.__dict__["transit_gateway_attachment_id"] = None
            __props__.__dict__["transit_gateway_id"] = None
        super(TransitGatewayConnect, __self__).__init__(
            'aws-native:ec2:TransitGatewayConnect',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'TransitGatewayConnect':
        """
        Get an existing TransitGatewayConnect resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = TransitGatewayConnectArgs.__new__(TransitGatewayConnectArgs)

        __props__.__dict__["creation_time"] = None
        __props__.__dict__["options"] = None
        __props__.__dict__["state"] = None
        __props__.__dict__["tags"] = None
        __props__.__dict__["transit_gateway_attachment_id"] = None
        __props__.__dict__["transit_gateway_id"] = None
        __props__.__dict__["transport_transit_gateway_attachment_id"] = None
        return TransitGatewayConnect(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="creationTime")
    def creation_time(self) -> pulumi.Output[str]:
        """
        The creation time.
        """
        return pulumi.get(self, "creation_time")

    @property
    @pulumi.getter
    def options(self) -> pulumi.Output['outputs.TransitGatewayConnectOptions']:
        """
        The Connect attachment options.
        """
        return pulumi.get(self, "options")

    @property
    @pulumi.getter
    def state(self) -> pulumi.Output[str]:
        """
        The state of the attachment.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Sequence['outputs.TransitGatewayConnectTag']]]:
        """
        The tags for the attachment.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="transitGatewayAttachmentId")
    def transit_gateway_attachment_id(self) -> pulumi.Output[str]:
        """
        The ID of the Connect attachment.
        """
        return pulumi.get(self, "transit_gateway_attachment_id")

    @property
    @pulumi.getter(name="transitGatewayId")
    def transit_gateway_id(self) -> pulumi.Output[str]:
        """
        The ID of the transit gateway.
        """
        return pulumi.get(self, "transit_gateway_id")

    @property
    @pulumi.getter(name="transportTransitGatewayAttachmentId")
    def transport_transit_gateway_attachment_id(self) -> pulumi.Output[str]:
        """
        The ID of the attachment from which the Connect attachment was created.
        """
        return pulumi.get(self, "transport_transit_gateway_attachment_id")

