# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ShareAccessArgs', 'ShareAccess']

@pulumi.input_type
class ShareAccessArgs:
    def __init__(__self__, *,
                 access_level: pulumi.Input[str],
                 access_to: pulumi.Input[str],
                 access_type: pulumi.Input[str],
                 share_id: pulumi.Input[str],
                 region: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ShareAccess resource.
        :param pulumi.Input[str] access_level: The access level to the share. Can either be `rw` or `ro`.
        :param pulumi.Input[str] access_to: The value that defines the access. Can either be an IP
               address or a username verified by configured Security Service of the Share Network.
        :param pulumi.Input[str] access_type: The access rule type. Can either be an ip, user,
               cert, or cephx. cephx support requires an OpenStack environment that supports
               Shared Filesystem microversion 2.13 (Mitaka) or later.
        :param pulumi.Input[str] share_id: The UUID of the share to which you are granted access.
        :param pulumi.Input[str] region: The region in which to obtain the V2 Shared File System client.
               A Shared File System client is needed to create a share access. Changing this
               creates a new share access.
        """
        pulumi.set(__self__, "access_level", access_level)
        pulumi.set(__self__, "access_to", access_to)
        pulumi.set(__self__, "access_type", access_type)
        pulumi.set(__self__, "share_id", share_id)
        if region is not None:
            pulumi.set(__self__, "region", region)

    @property
    @pulumi.getter(name="accessLevel")
    def access_level(self) -> pulumi.Input[str]:
        """
        The access level to the share. Can either be `rw` or `ro`.
        """
        return pulumi.get(self, "access_level")

    @access_level.setter
    def access_level(self, value: pulumi.Input[str]):
        pulumi.set(self, "access_level", value)

    @property
    @pulumi.getter(name="accessTo")
    def access_to(self) -> pulumi.Input[str]:
        """
        The value that defines the access. Can either be an IP
        address or a username verified by configured Security Service of the Share Network.
        """
        return pulumi.get(self, "access_to")

    @access_to.setter
    def access_to(self, value: pulumi.Input[str]):
        pulumi.set(self, "access_to", value)

    @property
    @pulumi.getter(name="accessType")
    def access_type(self) -> pulumi.Input[str]:
        """
        The access rule type. Can either be an ip, user,
        cert, or cephx. cephx support requires an OpenStack environment that supports
        Shared Filesystem microversion 2.13 (Mitaka) or later.
        """
        return pulumi.get(self, "access_type")

    @access_type.setter
    def access_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "access_type", value)

    @property
    @pulumi.getter(name="shareId")
    def share_id(self) -> pulumi.Input[str]:
        """
        The UUID of the share to which you are granted access.
        """
        return pulumi.get(self, "share_id")

    @share_id.setter
    def share_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "share_id", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to obtain the V2 Shared File System client.
        A Shared File System client is needed to create a share access. Changing this
        creates a new share access.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)


@pulumi.input_type
class _ShareAccessState:
    def __init__(__self__, *,
                 access_key: Optional[pulumi.Input[str]] = None,
                 access_level: Optional[pulumi.Input[str]] = None,
                 access_to: Optional[pulumi.Input[str]] = None,
                 access_type: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 share_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ShareAccess resources.
        :param pulumi.Input[str] access_key: The access credential of the entity granted access.
        :param pulumi.Input[str] access_level: The access level to the share. Can either be `rw` or `ro`.
        :param pulumi.Input[str] access_to: The value that defines the access. Can either be an IP
               address or a username verified by configured Security Service of the Share Network.
        :param pulumi.Input[str] access_type: The access rule type. Can either be an ip, user,
               cert, or cephx. cephx support requires an OpenStack environment that supports
               Shared Filesystem microversion 2.13 (Mitaka) or later.
        :param pulumi.Input[str] region: The region in which to obtain the V2 Shared File System client.
               A Shared File System client is needed to create a share access. Changing this
               creates a new share access.
        :param pulumi.Input[str] share_id: The UUID of the share to which you are granted access.
        """
        if access_key is not None:
            pulumi.set(__self__, "access_key", access_key)
        if access_level is not None:
            pulumi.set(__self__, "access_level", access_level)
        if access_to is not None:
            pulumi.set(__self__, "access_to", access_to)
        if access_type is not None:
            pulumi.set(__self__, "access_type", access_type)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if share_id is not None:
            pulumi.set(__self__, "share_id", share_id)

    @property
    @pulumi.getter(name="accessKey")
    def access_key(self) -> Optional[pulumi.Input[str]]:
        """
        The access credential of the entity granted access.
        """
        return pulumi.get(self, "access_key")

    @access_key.setter
    def access_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "access_key", value)

    @property
    @pulumi.getter(name="accessLevel")
    def access_level(self) -> Optional[pulumi.Input[str]]:
        """
        The access level to the share. Can either be `rw` or `ro`.
        """
        return pulumi.get(self, "access_level")

    @access_level.setter
    def access_level(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "access_level", value)

    @property
    @pulumi.getter(name="accessTo")
    def access_to(self) -> Optional[pulumi.Input[str]]:
        """
        The value that defines the access. Can either be an IP
        address or a username verified by configured Security Service of the Share Network.
        """
        return pulumi.get(self, "access_to")

    @access_to.setter
    def access_to(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "access_to", value)

    @property
    @pulumi.getter(name="accessType")
    def access_type(self) -> Optional[pulumi.Input[str]]:
        """
        The access rule type. Can either be an ip, user,
        cert, or cephx. cephx support requires an OpenStack environment that supports
        Shared Filesystem microversion 2.13 (Mitaka) or later.
        """
        return pulumi.get(self, "access_type")

    @access_type.setter
    def access_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "access_type", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to obtain the V2 Shared File System client.
        A Shared File System client is needed to create a share access. Changing this
        creates a new share access.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter(name="shareId")
    def share_id(self) -> Optional[pulumi.Input[str]]:
        """
        The UUID of the share to which you are granted access.
        """
        return pulumi.get(self, "share_id")

    @share_id.setter
    def share_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "share_id", value)


class ShareAccess(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 access_level: Optional[pulumi.Input[str]] = None,
                 access_to: Optional[pulumi.Input[str]] = None,
                 access_type: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 share_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        ## Example Usage
        ### NFS

        ```python
        import pulumi
        import pulumi_openstack as openstack

        network1 = openstack.networking.Network("network1", admin_state_up=True)
        subnet1 = openstack.networking.Subnet("subnet1",
            cidr="192.168.199.0/24",
            ip_version=4,
            network_id=network1.id)
        sharenetwork1 = openstack.sharedfilesystem.ShareNetwork("sharenetwork1",
            description="test share network with security services",
            neutron_net_id=network1.id,
            neutron_subnet_id=subnet1.id)
        share1 = openstack.sharedfilesystem.Share("share1",
            description="test share description",
            share_network_id=sharenetwork1.id,
            share_proto="NFS",
            size=1)
        share_access1 = openstack.sharedfilesystem.ShareAccess("shareAccess1",
            access_level="rw",
            access_to="192.168.199.10",
            access_type="ip",
            share_id=share1.id)
        ```
        ### CIFS

        ```python
        import pulumi
        import pulumi_openstack as openstack

        network1 = openstack.networking.Network("network1", admin_state_up=True)
        subnet1 = openstack.networking.Subnet("subnet1",
            cidr="192.168.199.0/24",
            ip_version=4,
            network_id=network1.id)
        securityservice1 = openstack.sharedfilesystem.SecurityService("securityservice1",
            description="created by terraform",
            dns_ip="192.168.199.10",
            domain="example.com",
            ou="CN=Computers,DC=example,DC=com",
            password="s8cret",
            server="192.168.199.10",
            type="active_directory",
            user="joinDomainUser")
        sharenetwork1 = openstack.sharedfilesystem.ShareNetwork("sharenetwork1",
            description="share the secure love",
            neutron_net_id=network1.id,
            neutron_subnet_id=subnet1.id,
            security_service_ids=[securityservice1.id])
        share1 = openstack.sharedfilesystem.Share("share1",
            share_network_id=sharenetwork1.id,
            share_proto="CIFS",
            size=1)
        share_access1 = openstack.sharedfilesystem.ShareAccess("shareAccess1",
            access_level="ro",
            access_to="windows",
            access_type="user",
            share_id=share1.id)
        share_access2 = openstack.sharedfilesystem.ShareAccess("shareAccess2",
            access_level="rw",
            access_to="linux",
            access_type="user",
            share_id=share1.id)
        pulumi.export("exportLocations", share1.export_locations)
        ```

        ## Import

        This resource can be imported by specifying the ID of the share and the ID of the share access, separated by a slash, e.g.

        ```sh
         $ pulumi import openstack:sharedfilesystem/shareAccess:ShareAccess share_access_1 <share id>/<share access id>
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] access_level: The access level to the share. Can either be `rw` or `ro`.
        :param pulumi.Input[str] access_to: The value that defines the access. Can either be an IP
               address or a username verified by configured Security Service of the Share Network.
        :param pulumi.Input[str] access_type: The access rule type. Can either be an ip, user,
               cert, or cephx. cephx support requires an OpenStack environment that supports
               Shared Filesystem microversion 2.13 (Mitaka) or later.
        :param pulumi.Input[str] region: The region in which to obtain the V2 Shared File System client.
               A Shared File System client is needed to create a share access. Changing this
               creates a new share access.
        :param pulumi.Input[str] share_id: The UUID of the share to which you are granted access.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ShareAccessArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        ## Example Usage
        ### NFS

        ```python
        import pulumi
        import pulumi_openstack as openstack

        network1 = openstack.networking.Network("network1", admin_state_up=True)
        subnet1 = openstack.networking.Subnet("subnet1",
            cidr="192.168.199.0/24",
            ip_version=4,
            network_id=network1.id)
        sharenetwork1 = openstack.sharedfilesystem.ShareNetwork("sharenetwork1",
            description="test share network with security services",
            neutron_net_id=network1.id,
            neutron_subnet_id=subnet1.id)
        share1 = openstack.sharedfilesystem.Share("share1",
            description="test share description",
            share_network_id=sharenetwork1.id,
            share_proto="NFS",
            size=1)
        share_access1 = openstack.sharedfilesystem.ShareAccess("shareAccess1",
            access_level="rw",
            access_to="192.168.199.10",
            access_type="ip",
            share_id=share1.id)
        ```
        ### CIFS

        ```python
        import pulumi
        import pulumi_openstack as openstack

        network1 = openstack.networking.Network("network1", admin_state_up=True)
        subnet1 = openstack.networking.Subnet("subnet1",
            cidr="192.168.199.0/24",
            ip_version=4,
            network_id=network1.id)
        securityservice1 = openstack.sharedfilesystem.SecurityService("securityservice1",
            description="created by terraform",
            dns_ip="192.168.199.10",
            domain="example.com",
            ou="CN=Computers,DC=example,DC=com",
            password="s8cret",
            server="192.168.199.10",
            type="active_directory",
            user="joinDomainUser")
        sharenetwork1 = openstack.sharedfilesystem.ShareNetwork("sharenetwork1",
            description="share the secure love",
            neutron_net_id=network1.id,
            neutron_subnet_id=subnet1.id,
            security_service_ids=[securityservice1.id])
        share1 = openstack.sharedfilesystem.Share("share1",
            share_network_id=sharenetwork1.id,
            share_proto="CIFS",
            size=1)
        share_access1 = openstack.sharedfilesystem.ShareAccess("shareAccess1",
            access_level="ro",
            access_to="windows",
            access_type="user",
            share_id=share1.id)
        share_access2 = openstack.sharedfilesystem.ShareAccess("shareAccess2",
            access_level="rw",
            access_to="linux",
            access_type="user",
            share_id=share1.id)
        pulumi.export("exportLocations", share1.export_locations)
        ```

        ## Import

        This resource can be imported by specifying the ID of the share and the ID of the share access, separated by a slash, e.g.

        ```sh
         $ pulumi import openstack:sharedfilesystem/shareAccess:ShareAccess share_access_1 <share id>/<share access id>
        ```

        :param str resource_name: The name of the resource.
        :param ShareAccessArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ShareAccessArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 access_level: Optional[pulumi.Input[str]] = None,
                 access_to: Optional[pulumi.Input[str]] = None,
                 access_type: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 share_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ShareAccessArgs.__new__(ShareAccessArgs)

            if access_level is None and not opts.urn:
                raise TypeError("Missing required property 'access_level'")
            __props__.__dict__["access_level"] = access_level
            if access_to is None and not opts.urn:
                raise TypeError("Missing required property 'access_to'")
            __props__.__dict__["access_to"] = access_to
            if access_type is None and not opts.urn:
                raise TypeError("Missing required property 'access_type'")
            __props__.__dict__["access_type"] = access_type
            __props__.__dict__["region"] = region
            if share_id is None and not opts.urn:
                raise TypeError("Missing required property 'share_id'")
            __props__.__dict__["share_id"] = share_id
            __props__.__dict__["access_key"] = None
        super(ShareAccess, __self__).__init__(
            'openstack:sharedfilesystem/shareAccess:ShareAccess',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            access_key: Optional[pulumi.Input[str]] = None,
            access_level: Optional[pulumi.Input[str]] = None,
            access_to: Optional[pulumi.Input[str]] = None,
            access_type: Optional[pulumi.Input[str]] = None,
            region: Optional[pulumi.Input[str]] = None,
            share_id: Optional[pulumi.Input[str]] = None) -> 'ShareAccess':
        """
        Get an existing ShareAccess resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] access_key: The access credential of the entity granted access.
        :param pulumi.Input[str] access_level: The access level to the share. Can either be `rw` or `ro`.
        :param pulumi.Input[str] access_to: The value that defines the access. Can either be an IP
               address or a username verified by configured Security Service of the Share Network.
        :param pulumi.Input[str] access_type: The access rule type. Can either be an ip, user,
               cert, or cephx. cephx support requires an OpenStack environment that supports
               Shared Filesystem microversion 2.13 (Mitaka) or later.
        :param pulumi.Input[str] region: The region in which to obtain the V2 Shared File System client.
               A Shared File System client is needed to create a share access. Changing this
               creates a new share access.
        :param pulumi.Input[str] share_id: The UUID of the share to which you are granted access.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ShareAccessState.__new__(_ShareAccessState)

        __props__.__dict__["access_key"] = access_key
        __props__.__dict__["access_level"] = access_level
        __props__.__dict__["access_to"] = access_to
        __props__.__dict__["access_type"] = access_type
        __props__.__dict__["region"] = region
        __props__.__dict__["share_id"] = share_id
        return ShareAccess(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="accessKey")
    def access_key(self) -> pulumi.Output[str]:
        """
        The access credential of the entity granted access.
        """
        return pulumi.get(self, "access_key")

    @property
    @pulumi.getter(name="accessLevel")
    def access_level(self) -> pulumi.Output[str]:
        """
        The access level to the share. Can either be `rw` or `ro`.
        """
        return pulumi.get(self, "access_level")

    @property
    @pulumi.getter(name="accessTo")
    def access_to(self) -> pulumi.Output[str]:
        """
        The value that defines the access. Can either be an IP
        address or a username verified by configured Security Service of the Share Network.
        """
        return pulumi.get(self, "access_to")

    @property
    @pulumi.getter(name="accessType")
    def access_type(self) -> pulumi.Output[str]:
        """
        The access rule type. Can either be an ip, user,
        cert, or cephx. cephx support requires an OpenStack environment that supports
        Shared Filesystem microversion 2.13 (Mitaka) or later.
        """
        return pulumi.get(self, "access_type")

    @property
    @pulumi.getter
    def region(self) -> pulumi.Output[str]:
        """
        The region in which to obtain the V2 Shared File System client.
        A Shared File System client is needed to create a share access. Changing this
        creates a new share access.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter(name="shareId")
    def share_id(self) -> pulumi.Output[str]:
        """
        The UUID of the share to which you are granted access.
        """
        return pulumi.get(self, "share_id")

