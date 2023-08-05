# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities
from . import outputs
from ._inputs import *

__all__ = ['FirewallArgs', 'Firewall']

@pulumi.input_type
class FirewallArgs:
    def __init__(__self__, *,
                 inbound_policy: pulumi.Input[str],
                 label: pulumi.Input[str],
                 outbound_policy: pulumi.Input[str],
                 disabled: Optional[pulumi.Input[bool]] = None,
                 inbounds: Optional[pulumi.Input[Sequence[pulumi.Input['FirewallInboundArgs']]]] = None,
                 linodes: Optional[pulumi.Input[Sequence[pulumi.Input[int]]]] = None,
                 outbounds: Optional[pulumi.Input[Sequence[pulumi.Input['FirewallOutboundArgs']]]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a Firewall resource.
        :param pulumi.Input[str] inbound_policy: The default behavior for inbound traffic. This setting can be overridden by updating the inbound.action property of the Firewall Rule. (`ACCEPT`, `DROP`)
        :param pulumi.Input[str] label: Used to identify this rule. For display purposes only.
        :param pulumi.Input[str] outbound_policy: The default behavior for outbound traffic. This setting can be overridden by updating the outbound.action property for an individual Firewall Rule. (`ACCEPT`, `DROP`)
        :param pulumi.Input[bool] disabled: If `true`, the Firewall's rules are not enforced (defaults to `false`).
        :param pulumi.Input[Sequence[pulumi.Input['FirewallInboundArgs']]] inbounds: A firewall rule that specifies what inbound network traffic is allowed.
        :param pulumi.Input[Sequence[pulumi.Input[int]]] linodes: A list of IDs of Linodes this Firewall should govern it's network traffic for.
        :param pulumi.Input[Sequence[pulumi.Input['FirewallOutboundArgs']]] outbounds: A firewall rule that specifies what outbound network traffic is allowed.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of tags applied to the Kubernetes cluster. Tags are for organizational purposes only.
        """
        pulumi.set(__self__, "inbound_policy", inbound_policy)
        pulumi.set(__self__, "label", label)
        pulumi.set(__self__, "outbound_policy", outbound_policy)
        if disabled is not None:
            pulumi.set(__self__, "disabled", disabled)
        if inbounds is not None:
            pulumi.set(__self__, "inbounds", inbounds)
        if linodes is not None:
            pulumi.set(__self__, "linodes", linodes)
        if outbounds is not None:
            pulumi.set(__self__, "outbounds", outbounds)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="inboundPolicy")
    def inbound_policy(self) -> pulumi.Input[str]:
        """
        The default behavior for inbound traffic. This setting can be overridden by updating the inbound.action property of the Firewall Rule. (`ACCEPT`, `DROP`)
        """
        return pulumi.get(self, "inbound_policy")

    @inbound_policy.setter
    def inbound_policy(self, value: pulumi.Input[str]):
        pulumi.set(self, "inbound_policy", value)

    @property
    @pulumi.getter
    def label(self) -> pulumi.Input[str]:
        """
        Used to identify this rule. For display purposes only.
        """
        return pulumi.get(self, "label")

    @label.setter
    def label(self, value: pulumi.Input[str]):
        pulumi.set(self, "label", value)

    @property
    @pulumi.getter(name="outboundPolicy")
    def outbound_policy(self) -> pulumi.Input[str]:
        """
        The default behavior for outbound traffic. This setting can be overridden by updating the outbound.action property for an individual Firewall Rule. (`ACCEPT`, `DROP`)
        """
        return pulumi.get(self, "outbound_policy")

    @outbound_policy.setter
    def outbound_policy(self, value: pulumi.Input[str]):
        pulumi.set(self, "outbound_policy", value)

    @property
    @pulumi.getter
    def disabled(self) -> Optional[pulumi.Input[bool]]:
        """
        If `true`, the Firewall's rules are not enforced (defaults to `false`).
        """
        return pulumi.get(self, "disabled")

    @disabled.setter
    def disabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "disabled", value)

    @property
    @pulumi.getter
    def inbounds(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['FirewallInboundArgs']]]]:
        """
        A firewall rule that specifies what inbound network traffic is allowed.
        """
        return pulumi.get(self, "inbounds")

    @inbounds.setter
    def inbounds(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['FirewallInboundArgs']]]]):
        pulumi.set(self, "inbounds", value)

    @property
    @pulumi.getter
    def linodes(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[int]]]]:
        """
        A list of IDs of Linodes this Firewall should govern it's network traffic for.
        """
        return pulumi.get(self, "linodes")

    @linodes.setter
    def linodes(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[int]]]]):
        pulumi.set(self, "linodes", value)

    @property
    @pulumi.getter
    def outbounds(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['FirewallOutboundArgs']]]]:
        """
        A firewall rule that specifies what outbound network traffic is allowed.
        """
        return pulumi.get(self, "outbounds")

    @outbounds.setter
    def outbounds(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['FirewallOutboundArgs']]]]):
        pulumi.set(self, "outbounds", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of tags applied to the Kubernetes cluster. Tags are for organizational purposes only.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _FirewallState:
    def __init__(__self__, *,
                 devices: Optional[pulumi.Input[Sequence[pulumi.Input['FirewallDeviceArgs']]]] = None,
                 disabled: Optional[pulumi.Input[bool]] = None,
                 inbound_policy: Optional[pulumi.Input[str]] = None,
                 inbounds: Optional[pulumi.Input[Sequence[pulumi.Input['FirewallInboundArgs']]]] = None,
                 label: Optional[pulumi.Input[str]] = None,
                 linodes: Optional[pulumi.Input[Sequence[pulumi.Input[int]]]] = None,
                 outbound_policy: Optional[pulumi.Input[str]] = None,
                 outbounds: Optional[pulumi.Input[Sequence[pulumi.Input['FirewallOutboundArgs']]]] = None,
                 status: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering Firewall resources.
        :param pulumi.Input[Sequence[pulumi.Input['FirewallDeviceArgs']]] devices: The devices associated with this firewall.
        :param pulumi.Input[bool] disabled: If `true`, the Firewall's rules are not enforced (defaults to `false`).
        :param pulumi.Input[str] inbound_policy: The default behavior for inbound traffic. This setting can be overridden by updating the inbound.action property of the Firewall Rule. (`ACCEPT`, `DROP`)
        :param pulumi.Input[Sequence[pulumi.Input['FirewallInboundArgs']]] inbounds: A firewall rule that specifies what inbound network traffic is allowed.
        :param pulumi.Input[str] label: Used to identify this rule. For display purposes only.
        :param pulumi.Input[Sequence[pulumi.Input[int]]] linodes: A list of IDs of Linodes this Firewall should govern it's network traffic for.
        :param pulumi.Input[str] outbound_policy: The default behavior for outbound traffic. This setting can be overridden by updating the outbound.action property for an individual Firewall Rule. (`ACCEPT`, `DROP`)
        :param pulumi.Input[Sequence[pulumi.Input['FirewallOutboundArgs']]] outbounds: A firewall rule that specifies what outbound network traffic is allowed.
        :param pulumi.Input[str] status: The status of the Firewall.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of tags applied to the Kubernetes cluster. Tags are for organizational purposes only.
        """
        if devices is not None:
            pulumi.set(__self__, "devices", devices)
        if disabled is not None:
            pulumi.set(__self__, "disabled", disabled)
        if inbound_policy is not None:
            pulumi.set(__self__, "inbound_policy", inbound_policy)
        if inbounds is not None:
            pulumi.set(__self__, "inbounds", inbounds)
        if label is not None:
            pulumi.set(__self__, "label", label)
        if linodes is not None:
            pulumi.set(__self__, "linodes", linodes)
        if outbound_policy is not None:
            pulumi.set(__self__, "outbound_policy", outbound_policy)
        if outbounds is not None:
            pulumi.set(__self__, "outbounds", outbounds)
        if status is not None:
            pulumi.set(__self__, "status", status)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter
    def devices(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['FirewallDeviceArgs']]]]:
        """
        The devices associated with this firewall.
        """
        return pulumi.get(self, "devices")

    @devices.setter
    def devices(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['FirewallDeviceArgs']]]]):
        pulumi.set(self, "devices", value)

    @property
    @pulumi.getter
    def disabled(self) -> Optional[pulumi.Input[bool]]:
        """
        If `true`, the Firewall's rules are not enforced (defaults to `false`).
        """
        return pulumi.get(self, "disabled")

    @disabled.setter
    def disabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "disabled", value)

    @property
    @pulumi.getter(name="inboundPolicy")
    def inbound_policy(self) -> Optional[pulumi.Input[str]]:
        """
        The default behavior for inbound traffic. This setting can be overridden by updating the inbound.action property of the Firewall Rule. (`ACCEPT`, `DROP`)
        """
        return pulumi.get(self, "inbound_policy")

    @inbound_policy.setter
    def inbound_policy(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "inbound_policy", value)

    @property
    @pulumi.getter
    def inbounds(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['FirewallInboundArgs']]]]:
        """
        A firewall rule that specifies what inbound network traffic is allowed.
        """
        return pulumi.get(self, "inbounds")

    @inbounds.setter
    def inbounds(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['FirewallInboundArgs']]]]):
        pulumi.set(self, "inbounds", value)

    @property
    @pulumi.getter
    def label(self) -> Optional[pulumi.Input[str]]:
        """
        Used to identify this rule. For display purposes only.
        """
        return pulumi.get(self, "label")

    @label.setter
    def label(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "label", value)

    @property
    @pulumi.getter
    def linodes(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[int]]]]:
        """
        A list of IDs of Linodes this Firewall should govern it's network traffic for.
        """
        return pulumi.get(self, "linodes")

    @linodes.setter
    def linodes(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[int]]]]):
        pulumi.set(self, "linodes", value)

    @property
    @pulumi.getter(name="outboundPolicy")
    def outbound_policy(self) -> Optional[pulumi.Input[str]]:
        """
        The default behavior for outbound traffic. This setting can be overridden by updating the outbound.action property for an individual Firewall Rule. (`ACCEPT`, `DROP`)
        """
        return pulumi.get(self, "outbound_policy")

    @outbound_policy.setter
    def outbound_policy(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "outbound_policy", value)

    @property
    @pulumi.getter
    def outbounds(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['FirewallOutboundArgs']]]]:
        """
        A firewall rule that specifies what outbound network traffic is allowed.
        """
        return pulumi.get(self, "outbounds")

    @outbounds.setter
    def outbounds(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['FirewallOutboundArgs']]]]):
        pulumi.set(self, "outbounds", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input[str]]:
        """
        The status of the Firewall.
        """
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "status", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of tags applied to the Kubernetes cluster. Tags are for organizational purposes only.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


class Firewall(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 disabled: Optional[pulumi.Input[bool]] = None,
                 inbound_policy: Optional[pulumi.Input[str]] = None,
                 inbounds: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallInboundArgs']]]]] = None,
                 label: Optional[pulumi.Input[str]] = None,
                 linodes: Optional[pulumi.Input[Sequence[pulumi.Input[int]]]] = None,
                 outbound_policy: Optional[pulumi.Input[str]] = None,
                 outbounds: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallOutboundArgs']]]]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Manages a Linode Firewall.

        ## Example Usage

        Accept only inbound HTTP(s) requests and drop outbound HTTP(s) requests:

        ```python
        import pulumi
        import pulumi_linode as linode

        my_instance = linode.Instance("myInstance",
            label="my_instance",
            image="linode/ubuntu18.04",
            region="us-southeast",
            type="g6-standard-1",
            root_pass="bogusPassword$",
            swap_size=256)
        my_firewall = linode.Firewall("myFirewall",
            label="my_firewall",
            inbounds=[
                linode.FirewallInboundArgs(
                    label="allow-http",
                    action="ACCEPT",
                    protocol="TCP",
                    ports="80",
                    ipv4s=["0.0.0.0/0"],
                    ipv6s=["::/0"],
                ),
                linode.FirewallInboundArgs(
                    label="allow-https",
                    action="ACCEPT",
                    protocol="TCP",
                    ports="443",
                    ipv4s=["0.0.0.0/0"],
                    ipv6s=["::/0"],
                ),
            ],
            inbound_policy="DROP",
            outbounds=[
                linode.FirewallOutboundArgs(
                    label="reject-http",
                    action="DROP",
                    protocol="TCP",
                    ports="80",
                    ipv4s=["0.0.0.0/0"],
                    ipv6s=["::/0"],
                ),
                linode.FirewallOutboundArgs(
                    label="reject-https",
                    action="DROP",
                    protocol="TCP",
                    ports="443",
                    ipv4s=["0.0.0.0/0"],
                    ipv6s=["::/0"],
                ),
            ],
            outbound_policy="ACCEPT",
            linodes=[my_instance.id])
        ```

        ## Import

        Firewalls can be imported using the `id`, e.g.

        ```sh
         $ pulumi import linode:index/firewall:Firewall my_firewall 12345
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[bool] disabled: If `true`, the Firewall's rules are not enforced (defaults to `false`).
        :param pulumi.Input[str] inbound_policy: The default behavior for inbound traffic. This setting can be overridden by updating the inbound.action property of the Firewall Rule. (`ACCEPT`, `DROP`)
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallInboundArgs']]]] inbounds: A firewall rule that specifies what inbound network traffic is allowed.
        :param pulumi.Input[str] label: Used to identify this rule. For display purposes only.
        :param pulumi.Input[Sequence[pulumi.Input[int]]] linodes: A list of IDs of Linodes this Firewall should govern it's network traffic for.
        :param pulumi.Input[str] outbound_policy: The default behavior for outbound traffic. This setting can be overridden by updating the outbound.action property for an individual Firewall Rule. (`ACCEPT`, `DROP`)
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallOutboundArgs']]]] outbounds: A firewall rule that specifies what outbound network traffic is allowed.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of tags applied to the Kubernetes cluster. Tags are for organizational purposes only.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: FirewallArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Linode Firewall.

        ## Example Usage

        Accept only inbound HTTP(s) requests and drop outbound HTTP(s) requests:

        ```python
        import pulumi
        import pulumi_linode as linode

        my_instance = linode.Instance("myInstance",
            label="my_instance",
            image="linode/ubuntu18.04",
            region="us-southeast",
            type="g6-standard-1",
            root_pass="bogusPassword$",
            swap_size=256)
        my_firewall = linode.Firewall("myFirewall",
            label="my_firewall",
            inbounds=[
                linode.FirewallInboundArgs(
                    label="allow-http",
                    action="ACCEPT",
                    protocol="TCP",
                    ports="80",
                    ipv4s=["0.0.0.0/0"],
                    ipv6s=["::/0"],
                ),
                linode.FirewallInboundArgs(
                    label="allow-https",
                    action="ACCEPT",
                    protocol="TCP",
                    ports="443",
                    ipv4s=["0.0.0.0/0"],
                    ipv6s=["::/0"],
                ),
            ],
            inbound_policy="DROP",
            outbounds=[
                linode.FirewallOutboundArgs(
                    label="reject-http",
                    action="DROP",
                    protocol="TCP",
                    ports="80",
                    ipv4s=["0.0.0.0/0"],
                    ipv6s=["::/0"],
                ),
                linode.FirewallOutboundArgs(
                    label="reject-https",
                    action="DROP",
                    protocol="TCP",
                    ports="443",
                    ipv4s=["0.0.0.0/0"],
                    ipv6s=["::/0"],
                ),
            ],
            outbound_policy="ACCEPT",
            linodes=[my_instance.id])
        ```

        ## Import

        Firewalls can be imported using the `id`, e.g.

        ```sh
         $ pulumi import linode:index/firewall:Firewall my_firewall 12345
        ```

        :param str resource_name: The name of the resource.
        :param FirewallArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(FirewallArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 disabled: Optional[pulumi.Input[bool]] = None,
                 inbound_policy: Optional[pulumi.Input[str]] = None,
                 inbounds: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallInboundArgs']]]]] = None,
                 label: Optional[pulumi.Input[str]] = None,
                 linodes: Optional[pulumi.Input[Sequence[pulumi.Input[int]]]] = None,
                 outbound_policy: Optional[pulumi.Input[str]] = None,
                 outbounds: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallOutboundArgs']]]]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = FirewallArgs.__new__(FirewallArgs)

            __props__.__dict__["disabled"] = disabled
            if inbound_policy is None and not opts.urn:
                raise TypeError("Missing required property 'inbound_policy'")
            __props__.__dict__["inbound_policy"] = inbound_policy
            __props__.__dict__["inbounds"] = inbounds
            if label is None and not opts.urn:
                raise TypeError("Missing required property 'label'")
            __props__.__dict__["label"] = label
            __props__.__dict__["linodes"] = linodes
            if outbound_policy is None and not opts.urn:
                raise TypeError("Missing required property 'outbound_policy'")
            __props__.__dict__["outbound_policy"] = outbound_policy
            __props__.__dict__["outbounds"] = outbounds
            __props__.__dict__["tags"] = tags
            __props__.__dict__["devices"] = None
            __props__.__dict__["status"] = None
        super(Firewall, __self__).__init__(
            'linode:index/firewall:Firewall',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            devices: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallDeviceArgs']]]]] = None,
            disabled: Optional[pulumi.Input[bool]] = None,
            inbound_policy: Optional[pulumi.Input[str]] = None,
            inbounds: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallInboundArgs']]]]] = None,
            label: Optional[pulumi.Input[str]] = None,
            linodes: Optional[pulumi.Input[Sequence[pulumi.Input[int]]]] = None,
            outbound_policy: Optional[pulumi.Input[str]] = None,
            outbounds: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallOutboundArgs']]]]] = None,
            status: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None) -> 'Firewall':
        """
        Get an existing Firewall resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallDeviceArgs']]]] devices: The devices associated with this firewall.
        :param pulumi.Input[bool] disabled: If `true`, the Firewall's rules are not enforced (defaults to `false`).
        :param pulumi.Input[str] inbound_policy: The default behavior for inbound traffic. This setting can be overridden by updating the inbound.action property of the Firewall Rule. (`ACCEPT`, `DROP`)
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallInboundArgs']]]] inbounds: A firewall rule that specifies what inbound network traffic is allowed.
        :param pulumi.Input[str] label: Used to identify this rule. For display purposes only.
        :param pulumi.Input[Sequence[pulumi.Input[int]]] linodes: A list of IDs of Linodes this Firewall should govern it's network traffic for.
        :param pulumi.Input[str] outbound_policy: The default behavior for outbound traffic. This setting can be overridden by updating the outbound.action property for an individual Firewall Rule. (`ACCEPT`, `DROP`)
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FirewallOutboundArgs']]]] outbounds: A firewall rule that specifies what outbound network traffic is allowed.
        :param pulumi.Input[str] status: The status of the Firewall.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of tags applied to the Kubernetes cluster. Tags are for organizational purposes only.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _FirewallState.__new__(_FirewallState)

        __props__.__dict__["devices"] = devices
        __props__.__dict__["disabled"] = disabled
        __props__.__dict__["inbound_policy"] = inbound_policy
        __props__.__dict__["inbounds"] = inbounds
        __props__.__dict__["label"] = label
        __props__.__dict__["linodes"] = linodes
        __props__.__dict__["outbound_policy"] = outbound_policy
        __props__.__dict__["outbounds"] = outbounds
        __props__.__dict__["status"] = status
        __props__.__dict__["tags"] = tags
        return Firewall(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def devices(self) -> pulumi.Output[Sequence['outputs.FirewallDevice']]:
        """
        The devices associated with this firewall.
        """
        return pulumi.get(self, "devices")

    @property
    @pulumi.getter
    def disabled(self) -> pulumi.Output[Optional[bool]]:
        """
        If `true`, the Firewall's rules are not enforced (defaults to `false`).
        """
        return pulumi.get(self, "disabled")

    @property
    @pulumi.getter(name="inboundPolicy")
    def inbound_policy(self) -> pulumi.Output[str]:
        """
        The default behavior for inbound traffic. This setting can be overridden by updating the inbound.action property of the Firewall Rule. (`ACCEPT`, `DROP`)
        """
        return pulumi.get(self, "inbound_policy")

    @property
    @pulumi.getter
    def inbounds(self) -> pulumi.Output[Optional[Sequence['outputs.FirewallInbound']]]:
        """
        A firewall rule that specifies what inbound network traffic is allowed.
        """
        return pulumi.get(self, "inbounds")

    @property
    @pulumi.getter
    def label(self) -> pulumi.Output[str]:
        """
        Used to identify this rule. For display purposes only.
        """
        return pulumi.get(self, "label")

    @property
    @pulumi.getter
    def linodes(self) -> pulumi.Output[Sequence[int]]:
        """
        A list of IDs of Linodes this Firewall should govern it's network traffic for.
        """
        return pulumi.get(self, "linodes")

    @property
    @pulumi.getter(name="outboundPolicy")
    def outbound_policy(self) -> pulumi.Output[str]:
        """
        The default behavior for outbound traffic. This setting can be overridden by updating the outbound.action property for an individual Firewall Rule. (`ACCEPT`, `DROP`)
        """
        return pulumi.get(self, "outbound_policy")

    @property
    @pulumi.getter
    def outbounds(self) -> pulumi.Output[Optional[Sequence['outputs.FirewallOutbound']]]:
        """
        A firewall rule that specifies what outbound network traffic is allowed.
        """
        return pulumi.get(self, "outbounds")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output[str]:
        """
        The status of the Firewall.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        A list of tags applied to the Kubernetes cluster. Tags are for organizational purposes only.
        """
        return pulumi.get(self, "tags")

