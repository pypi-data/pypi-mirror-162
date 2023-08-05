# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['QosAssociationV3Args', 'QosAssociationV3']

@pulumi.input_type
class QosAssociationV3Args:
    def __init__(__self__, *,
                 qos_id: pulumi.Input[str],
                 volume_type_id: pulumi.Input[str],
                 region: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a QosAssociationV3 resource.
        :param pulumi.Input[str] qos_id: ID of the qos to associate. Changing this creates
               a new qos association.
        :param pulumi.Input[str] volume_type_id: ID of the volume_type to associate.
               Changing this creates a new qos association.
        :param pulumi.Input[str] region: The region in which to create the qos association.
               If omitted, the `region` argument of the provider is used. Changing
               this creates a new qos association.
        """
        pulumi.set(__self__, "qos_id", qos_id)
        pulumi.set(__self__, "volume_type_id", volume_type_id)
        if region is not None:
            pulumi.set(__self__, "region", region)

    @property
    @pulumi.getter(name="qosId")
    def qos_id(self) -> pulumi.Input[str]:
        """
        ID of the qos to associate. Changing this creates
        a new qos association.
        """
        return pulumi.get(self, "qos_id")

    @qos_id.setter
    def qos_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "qos_id", value)

    @property
    @pulumi.getter(name="volumeTypeId")
    def volume_type_id(self) -> pulumi.Input[str]:
        """
        ID of the volume_type to associate.
        Changing this creates a new qos association.
        """
        return pulumi.get(self, "volume_type_id")

    @volume_type_id.setter
    def volume_type_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "volume_type_id", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to create the qos association.
        If omitted, the `region` argument of the provider is used. Changing
        this creates a new qos association.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)


@pulumi.input_type
class _QosAssociationV3State:
    def __init__(__self__, *,
                 qos_id: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 volume_type_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering QosAssociationV3 resources.
        :param pulumi.Input[str] qos_id: ID of the qos to associate. Changing this creates
               a new qos association.
        :param pulumi.Input[str] region: The region in which to create the qos association.
               If omitted, the `region` argument of the provider is used. Changing
               this creates a new qos association.
        :param pulumi.Input[str] volume_type_id: ID of the volume_type to associate.
               Changing this creates a new qos association.
        """
        if qos_id is not None:
            pulumi.set(__self__, "qos_id", qos_id)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if volume_type_id is not None:
            pulumi.set(__self__, "volume_type_id", volume_type_id)

    @property
    @pulumi.getter(name="qosId")
    def qos_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the qos to associate. Changing this creates
        a new qos association.
        """
        return pulumi.get(self, "qos_id")

    @qos_id.setter
    def qos_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "qos_id", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to create the qos association.
        If omitted, the `region` argument of the provider is used. Changing
        this creates a new qos association.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter(name="volumeTypeId")
    def volume_type_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the volume_type to associate.
        Changing this creates a new qos association.
        """
        return pulumi.get(self, "volume_type_id")

    @volume_type_id.setter
    def volume_type_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "volume_type_id", value)


class QosAssociationV3(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 qos_id: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 volume_type_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages a V3 block storage Qos Association resource within OpenStack.

        > **Note:** This usually requires admin privileges.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_openstack as openstack

        qos = openstack.blockstorage.QosV3("qos",
            consumer="front-end",
            specs={
                "read_iops_sec": "20000",
            })
        volume_type = openstack.blockstorage.VolumeTypeV3("volumeType")
        qos_association = openstack.blockstorage.QosAssociationV3("qosAssociation",
            qos_id=qos.id,
            volume_type_id=volume_type.id)
        ```

        ## Import

        Qos association can be imported using the `qos_id/volume_type_id`, e.g.

        ```sh
         $ pulumi import openstack:blockstorage/qosAssociationV3:QosAssociationV3 qos_association 941793f0-0a34-4bc4-b72e-a6326ae58283/ea257959-eeb1-4c10-8d33-26f0409a755d
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] qos_id: ID of the qos to associate. Changing this creates
               a new qos association.
        :param pulumi.Input[str] region: The region in which to create the qos association.
               If omitted, the `region` argument of the provider is used. Changing
               this creates a new qos association.
        :param pulumi.Input[str] volume_type_id: ID of the volume_type to associate.
               Changing this creates a new qos association.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: QosAssociationV3Args,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a V3 block storage Qos Association resource within OpenStack.

        > **Note:** This usually requires admin privileges.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_openstack as openstack

        qos = openstack.blockstorage.QosV3("qos",
            consumer="front-end",
            specs={
                "read_iops_sec": "20000",
            })
        volume_type = openstack.blockstorage.VolumeTypeV3("volumeType")
        qos_association = openstack.blockstorage.QosAssociationV3("qosAssociation",
            qos_id=qos.id,
            volume_type_id=volume_type.id)
        ```

        ## Import

        Qos association can be imported using the `qos_id/volume_type_id`, e.g.

        ```sh
         $ pulumi import openstack:blockstorage/qosAssociationV3:QosAssociationV3 qos_association 941793f0-0a34-4bc4-b72e-a6326ae58283/ea257959-eeb1-4c10-8d33-26f0409a755d
        ```

        :param str resource_name: The name of the resource.
        :param QosAssociationV3Args args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(QosAssociationV3Args, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 qos_id: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 volume_type_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = QosAssociationV3Args.__new__(QosAssociationV3Args)

            if qos_id is None and not opts.urn:
                raise TypeError("Missing required property 'qos_id'")
            __props__.__dict__["qos_id"] = qos_id
            __props__.__dict__["region"] = region
            if volume_type_id is None and not opts.urn:
                raise TypeError("Missing required property 'volume_type_id'")
            __props__.__dict__["volume_type_id"] = volume_type_id
        super(QosAssociationV3, __self__).__init__(
            'openstack:blockstorage/qosAssociationV3:QosAssociationV3',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            qos_id: Optional[pulumi.Input[str]] = None,
            region: Optional[pulumi.Input[str]] = None,
            volume_type_id: Optional[pulumi.Input[str]] = None) -> 'QosAssociationV3':
        """
        Get an existing QosAssociationV3 resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] qos_id: ID of the qos to associate. Changing this creates
               a new qos association.
        :param pulumi.Input[str] region: The region in which to create the qos association.
               If omitted, the `region` argument of the provider is used. Changing
               this creates a new qos association.
        :param pulumi.Input[str] volume_type_id: ID of the volume_type to associate.
               Changing this creates a new qos association.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _QosAssociationV3State.__new__(_QosAssociationV3State)

        __props__.__dict__["qos_id"] = qos_id
        __props__.__dict__["region"] = region
        __props__.__dict__["volume_type_id"] = volume_type_id
        return QosAssociationV3(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="qosId")
    def qos_id(self) -> pulumi.Output[str]:
        """
        ID of the qos to associate. Changing this creates
        a new qos association.
        """
        return pulumi.get(self, "qos_id")

    @property
    @pulumi.getter
    def region(self) -> pulumi.Output[str]:
        """
        The region in which to create the qos association.
        If omitted, the `region` argument of the provider is used. Changing
        this creates a new qos association.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter(name="volumeTypeId")
    def volume_type_id(self) -> pulumi.Output[str]:
        """
        ID of the volume_type to associate.
        Changing this creates a new qos association.
        """
        return pulumi.get(self, "volume_type_id")

