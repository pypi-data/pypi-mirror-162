# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['SecGroupArgs', 'SecGroup']

@pulumi.input_type
class SecGroupArgs:
    def __init__(__self__, *,
                 delete_default_rules: Optional[pulumi.Input[bool]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 tenant_id: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a SecGroup resource.
        :param pulumi.Input[bool] delete_default_rules: Whether or not to delete the default
               egress security rules. This is `false` by default. See the below note
               for more information.
        :param pulumi.Input[str] description: A unique name for the security group.
        :param pulumi.Input[str] name: A unique name for the security group.
        :param pulumi.Input[str] region: The region in which to obtain the V2 networking client.
               A networking client is needed to create a port. If omitted, the
               `region` argument of the provider is used. Changing this creates a new
               security group.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A set of string tags for the security group.
        :param pulumi.Input[str] tenant_id: The owner of the security group. Required if admin
               wants to create a port for another tenant. Changing this creates a new
               security group.
        """
        if delete_default_rules is not None:
            pulumi.set(__self__, "delete_default_rules", delete_default_rules)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tenant_id is not None:
            pulumi.set(__self__, "tenant_id", tenant_id)

    @property
    @pulumi.getter(name="deleteDefaultRules")
    def delete_default_rules(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether or not to delete the default
        egress security rules. This is `false` by default. See the below note
        for more information.
        """
        return pulumi.get(self, "delete_default_rules")

    @delete_default_rules.setter
    def delete_default_rules(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "delete_default_rules", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A unique name for the security group.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        A unique name for the security group.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to obtain the V2 networking client.
        A networking client is needed to create a port. If omitted, the
        `region` argument of the provider is used. Changing this creates a new
        security group.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A set of string tags for the security group.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="tenantId")
    def tenant_id(self) -> Optional[pulumi.Input[str]]:
        """
        The owner of the security group. Required if admin
        wants to create a port for another tenant. Changing this creates a new
        security group.
        """
        return pulumi.get(self, "tenant_id")

    @tenant_id.setter
    def tenant_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "tenant_id", value)


@pulumi.input_type
class _SecGroupState:
    def __init__(__self__, *,
                 all_tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 delete_default_rules: Optional[pulumi.Input[bool]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 tenant_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering SecGroup resources.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] all_tags: The collection of tags assigned on the security group, which have
               been explicitly and implicitly added.
        :param pulumi.Input[bool] delete_default_rules: Whether or not to delete the default
               egress security rules. This is `false` by default. See the below note
               for more information.
        :param pulumi.Input[str] description: A unique name for the security group.
        :param pulumi.Input[str] name: A unique name for the security group.
        :param pulumi.Input[str] region: The region in which to obtain the V2 networking client.
               A networking client is needed to create a port. If omitted, the
               `region` argument of the provider is used. Changing this creates a new
               security group.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A set of string tags for the security group.
        :param pulumi.Input[str] tenant_id: The owner of the security group. Required if admin
               wants to create a port for another tenant. Changing this creates a new
               security group.
        """
        if all_tags is not None:
            pulumi.set(__self__, "all_tags", all_tags)
        if delete_default_rules is not None:
            pulumi.set(__self__, "delete_default_rules", delete_default_rules)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tenant_id is not None:
            pulumi.set(__self__, "tenant_id", tenant_id)

    @property
    @pulumi.getter(name="allTags")
    def all_tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The collection of tags assigned on the security group, which have
        been explicitly and implicitly added.
        """
        return pulumi.get(self, "all_tags")

    @all_tags.setter
    def all_tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "all_tags", value)

    @property
    @pulumi.getter(name="deleteDefaultRules")
    def delete_default_rules(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether or not to delete the default
        egress security rules. This is `false` by default. See the below note
        for more information.
        """
        return pulumi.get(self, "delete_default_rules")

    @delete_default_rules.setter
    def delete_default_rules(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "delete_default_rules", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A unique name for the security group.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        A unique name for the security group.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to obtain the V2 networking client.
        A networking client is needed to create a port. If omitted, the
        `region` argument of the provider is used. Changing this creates a new
        security group.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A set of string tags for the security group.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="tenantId")
    def tenant_id(self) -> Optional[pulumi.Input[str]]:
        """
        The owner of the security group. Required if admin
        wants to create a port for another tenant. Changing this creates a new
        security group.
        """
        return pulumi.get(self, "tenant_id")

    @tenant_id.setter
    def tenant_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "tenant_id", value)


class SecGroup(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 delete_default_rules: Optional[pulumi.Input[bool]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 tenant_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        ## Import

        Security Groups can be imported using the `id`, e.g.

        ```sh
         $ pulumi import openstack:networking/secGroup:SecGroup secgroup_1 38809219-5e8a-4852-9139-6f461c90e8bc
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[bool] delete_default_rules: Whether or not to delete the default
               egress security rules. This is `false` by default. See the below note
               for more information.
        :param pulumi.Input[str] description: A unique name for the security group.
        :param pulumi.Input[str] name: A unique name for the security group.
        :param pulumi.Input[str] region: The region in which to obtain the V2 networking client.
               A networking client is needed to create a port. If omitted, the
               `region` argument of the provider is used. Changing this creates a new
               security group.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A set of string tags for the security group.
        :param pulumi.Input[str] tenant_id: The owner of the security group. Required if admin
               wants to create a port for another tenant. Changing this creates a new
               security group.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[SecGroupArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        ## Import

        Security Groups can be imported using the `id`, e.g.

        ```sh
         $ pulumi import openstack:networking/secGroup:SecGroup secgroup_1 38809219-5e8a-4852-9139-6f461c90e8bc
        ```

        :param str resource_name: The name of the resource.
        :param SecGroupArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(SecGroupArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 delete_default_rules: Optional[pulumi.Input[bool]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 tenant_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = SecGroupArgs.__new__(SecGroupArgs)

            __props__.__dict__["delete_default_rules"] = delete_default_rules
            __props__.__dict__["description"] = description
            __props__.__dict__["name"] = name
            __props__.__dict__["region"] = region
            __props__.__dict__["tags"] = tags
            __props__.__dict__["tenant_id"] = tenant_id
            __props__.__dict__["all_tags"] = None
        super(SecGroup, __self__).__init__(
            'openstack:networking/secGroup:SecGroup',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            all_tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            delete_default_rules: Optional[pulumi.Input[bool]] = None,
            description: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            region: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            tenant_id: Optional[pulumi.Input[str]] = None) -> 'SecGroup':
        """
        Get an existing SecGroup resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] all_tags: The collection of tags assigned on the security group, which have
               been explicitly and implicitly added.
        :param pulumi.Input[bool] delete_default_rules: Whether or not to delete the default
               egress security rules. This is `false` by default. See the below note
               for more information.
        :param pulumi.Input[str] description: A unique name for the security group.
        :param pulumi.Input[str] name: A unique name for the security group.
        :param pulumi.Input[str] region: The region in which to obtain the V2 networking client.
               A networking client is needed to create a port. If omitted, the
               `region` argument of the provider is used. Changing this creates a new
               security group.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A set of string tags for the security group.
        :param pulumi.Input[str] tenant_id: The owner of the security group. Required if admin
               wants to create a port for another tenant. Changing this creates a new
               security group.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _SecGroupState.__new__(_SecGroupState)

        __props__.__dict__["all_tags"] = all_tags
        __props__.__dict__["delete_default_rules"] = delete_default_rules
        __props__.__dict__["description"] = description
        __props__.__dict__["name"] = name
        __props__.__dict__["region"] = region
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tenant_id"] = tenant_id
        return SecGroup(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="allTags")
    def all_tags(self) -> pulumi.Output[Sequence[str]]:
        """
        The collection of tags assigned on the security group, which have
        been explicitly and implicitly added.
        """
        return pulumi.get(self, "all_tags")

    @property
    @pulumi.getter(name="deleteDefaultRules")
    def delete_default_rules(self) -> pulumi.Output[Optional[bool]]:
        """
        Whether or not to delete the default
        egress security rules. This is `false` by default. See the below note
        for more information.
        """
        return pulumi.get(self, "delete_default_rules")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        A unique name for the security group.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        A unique name for the security group.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def region(self) -> pulumi.Output[str]:
        """
        The region in which to obtain the V2 networking client.
        A networking client is needed to create a port. If omitted, the
        `region` argument of the provider is used. Changing this creates a new
        security group.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        A set of string tags for the security group.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="tenantId")
    def tenant_id(self) -> pulumi.Output[str]:
        """
        The owner of the security group. Required if admin
        wants to create a port for another tenant. Changing this creates a new
        security group.
        """
        return pulumi.get(self, "tenant_id")

