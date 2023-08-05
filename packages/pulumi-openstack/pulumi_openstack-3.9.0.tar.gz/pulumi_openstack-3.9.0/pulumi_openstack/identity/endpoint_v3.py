# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['EndpointV3Args', 'EndpointV3']

@pulumi.input_type
class EndpointV3Args:
    def __init__(__self__, *,
                 endpoint_region: pulumi.Input[str],
                 service_id: pulumi.Input[str],
                 url: pulumi.Input[str],
                 interface: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a EndpointV3 resource.
        :param pulumi.Input[str] endpoint_region: The endpoint region. The `region` and
               `endpoint_region` can be different.
        :param pulumi.Input[str] service_id: The endpoint service ID.
        :param pulumi.Input[str] url: The endpoint url.
        :param pulumi.Input[str] interface: The endpoint interface. Valid values are `public`,
               `internal` and `admin`. Default value is `public`
        :param pulumi.Input[str] name: The endpoint name.
        :param pulumi.Input[str] region: The region in which to obtain the V3 Keystone client.
               If omitted, the `region` argument of the provider is used.
        """
        pulumi.set(__self__, "endpoint_region", endpoint_region)
        pulumi.set(__self__, "service_id", service_id)
        pulumi.set(__self__, "url", url)
        if interface is not None:
            pulumi.set(__self__, "interface", interface)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if region is not None:
            pulumi.set(__self__, "region", region)

    @property
    @pulumi.getter(name="endpointRegion")
    def endpoint_region(self) -> pulumi.Input[str]:
        """
        The endpoint region. The `region` and
        `endpoint_region` can be different.
        """
        return pulumi.get(self, "endpoint_region")

    @endpoint_region.setter
    def endpoint_region(self, value: pulumi.Input[str]):
        pulumi.set(self, "endpoint_region", value)

    @property
    @pulumi.getter(name="serviceId")
    def service_id(self) -> pulumi.Input[str]:
        """
        The endpoint service ID.
        """
        return pulumi.get(self, "service_id")

    @service_id.setter
    def service_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "service_id", value)

    @property
    @pulumi.getter
    def url(self) -> pulumi.Input[str]:
        """
        The endpoint url.
        """
        return pulumi.get(self, "url")

    @url.setter
    def url(self, value: pulumi.Input[str]):
        pulumi.set(self, "url", value)

    @property
    @pulumi.getter
    def interface(self) -> Optional[pulumi.Input[str]]:
        """
        The endpoint interface. Valid values are `public`,
        `internal` and `admin`. Default value is `public`
        """
        return pulumi.get(self, "interface")

    @interface.setter
    def interface(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "interface", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The endpoint name.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to obtain the V3 Keystone client.
        If omitted, the `region` argument of the provider is used.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)


@pulumi.input_type
class _EndpointV3State:
    def __init__(__self__, *,
                 endpoint_region: Optional[pulumi.Input[str]] = None,
                 interface: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 service_id: Optional[pulumi.Input[str]] = None,
                 service_name: Optional[pulumi.Input[str]] = None,
                 service_type: Optional[pulumi.Input[str]] = None,
                 url: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering EndpointV3 resources.
        :param pulumi.Input[str] endpoint_region: The endpoint region. The `region` and
               `endpoint_region` can be different.
        :param pulumi.Input[str] interface: The endpoint interface. Valid values are `public`,
               `internal` and `admin`. Default value is `public`
        :param pulumi.Input[str] name: The endpoint name.
        :param pulumi.Input[str] region: The region in which to obtain the V3 Keystone client.
               If omitted, the `region` argument of the provider is used.
        :param pulumi.Input[str] service_id: The endpoint service ID.
        :param pulumi.Input[str] service_name: The service name of the endpoint.
        :param pulumi.Input[str] service_type: The service type of the endpoint.
        :param pulumi.Input[str] url: The endpoint url.
        """
        if endpoint_region is not None:
            pulumi.set(__self__, "endpoint_region", endpoint_region)
        if interface is not None:
            pulumi.set(__self__, "interface", interface)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if service_id is not None:
            pulumi.set(__self__, "service_id", service_id)
        if service_name is not None:
            pulumi.set(__self__, "service_name", service_name)
        if service_type is not None:
            pulumi.set(__self__, "service_type", service_type)
        if url is not None:
            pulumi.set(__self__, "url", url)

    @property
    @pulumi.getter(name="endpointRegion")
    def endpoint_region(self) -> Optional[pulumi.Input[str]]:
        """
        The endpoint region. The `region` and
        `endpoint_region` can be different.
        """
        return pulumi.get(self, "endpoint_region")

    @endpoint_region.setter
    def endpoint_region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "endpoint_region", value)

    @property
    @pulumi.getter
    def interface(self) -> Optional[pulumi.Input[str]]:
        """
        The endpoint interface. Valid values are `public`,
        `internal` and `admin`. Default value is `public`
        """
        return pulumi.get(self, "interface")

    @interface.setter
    def interface(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "interface", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The endpoint name.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to obtain the V3 Keystone client.
        If omitted, the `region` argument of the provider is used.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter(name="serviceId")
    def service_id(self) -> Optional[pulumi.Input[str]]:
        """
        The endpoint service ID.
        """
        return pulumi.get(self, "service_id")

    @service_id.setter
    def service_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "service_id", value)

    @property
    @pulumi.getter(name="serviceName")
    def service_name(self) -> Optional[pulumi.Input[str]]:
        """
        The service name of the endpoint.
        """
        return pulumi.get(self, "service_name")

    @service_name.setter
    def service_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "service_name", value)

    @property
    @pulumi.getter(name="serviceType")
    def service_type(self) -> Optional[pulumi.Input[str]]:
        """
        The service type of the endpoint.
        """
        return pulumi.get(self, "service_type")

    @service_type.setter
    def service_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "service_type", value)

    @property
    @pulumi.getter
    def url(self) -> Optional[pulumi.Input[str]]:
        """
        The endpoint url.
        """
        return pulumi.get(self, "url")

    @url.setter
    def url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "url", value)


class EndpointV3(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 endpoint_region: Optional[pulumi.Input[str]] = None,
                 interface: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 service_id: Optional[pulumi.Input[str]] = None,
                 url: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages a V3 Endpoint resource within OpenStack Keystone.

        > **Note:** This usually requires admin privileges.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_openstack as openstack

        service1 = openstack.identity.ServiceV3("service1", type="my-service-type")
        endpoint1 = openstack.identity.EndpointV3("endpoint1",
            endpoint_region=service1.region,
            service_id=service1.id,
            url="http://my-endpoint")
        ```

        ## Import

        Endpoints can be imported using the `id`, e.g.

        ```sh
         $ pulumi import openstack:identity/endpointV3:EndpointV3 endpoint_1 5392472b-106a-4845-90c6-7c8445f18770
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] endpoint_region: The endpoint region. The `region` and
               `endpoint_region` can be different.
        :param pulumi.Input[str] interface: The endpoint interface. Valid values are `public`,
               `internal` and `admin`. Default value is `public`
        :param pulumi.Input[str] name: The endpoint name.
        :param pulumi.Input[str] region: The region in which to obtain the V3 Keystone client.
               If omitted, the `region` argument of the provider is used.
        :param pulumi.Input[str] service_id: The endpoint service ID.
        :param pulumi.Input[str] url: The endpoint url.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: EndpointV3Args,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a V3 Endpoint resource within OpenStack Keystone.

        > **Note:** This usually requires admin privileges.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_openstack as openstack

        service1 = openstack.identity.ServiceV3("service1", type="my-service-type")
        endpoint1 = openstack.identity.EndpointV3("endpoint1",
            endpoint_region=service1.region,
            service_id=service1.id,
            url="http://my-endpoint")
        ```

        ## Import

        Endpoints can be imported using the `id`, e.g.

        ```sh
         $ pulumi import openstack:identity/endpointV3:EndpointV3 endpoint_1 5392472b-106a-4845-90c6-7c8445f18770
        ```

        :param str resource_name: The name of the resource.
        :param EndpointV3Args args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(EndpointV3Args, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 endpoint_region: Optional[pulumi.Input[str]] = None,
                 interface: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 service_id: Optional[pulumi.Input[str]] = None,
                 url: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = EndpointV3Args.__new__(EndpointV3Args)

            if endpoint_region is None and not opts.urn:
                raise TypeError("Missing required property 'endpoint_region'")
            __props__.__dict__["endpoint_region"] = endpoint_region
            __props__.__dict__["interface"] = interface
            __props__.__dict__["name"] = name
            __props__.__dict__["region"] = region
            if service_id is None and not opts.urn:
                raise TypeError("Missing required property 'service_id'")
            __props__.__dict__["service_id"] = service_id
            if url is None and not opts.urn:
                raise TypeError("Missing required property 'url'")
            __props__.__dict__["url"] = url
            __props__.__dict__["service_name"] = None
            __props__.__dict__["service_type"] = None
        super(EndpointV3, __self__).__init__(
            'openstack:identity/endpointV3:EndpointV3',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            endpoint_region: Optional[pulumi.Input[str]] = None,
            interface: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            region: Optional[pulumi.Input[str]] = None,
            service_id: Optional[pulumi.Input[str]] = None,
            service_name: Optional[pulumi.Input[str]] = None,
            service_type: Optional[pulumi.Input[str]] = None,
            url: Optional[pulumi.Input[str]] = None) -> 'EndpointV3':
        """
        Get an existing EndpointV3 resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] endpoint_region: The endpoint region. The `region` and
               `endpoint_region` can be different.
        :param pulumi.Input[str] interface: The endpoint interface. Valid values are `public`,
               `internal` and `admin`. Default value is `public`
        :param pulumi.Input[str] name: The endpoint name.
        :param pulumi.Input[str] region: The region in which to obtain the V3 Keystone client.
               If omitted, the `region` argument of the provider is used.
        :param pulumi.Input[str] service_id: The endpoint service ID.
        :param pulumi.Input[str] service_name: The service name of the endpoint.
        :param pulumi.Input[str] service_type: The service type of the endpoint.
        :param pulumi.Input[str] url: The endpoint url.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _EndpointV3State.__new__(_EndpointV3State)

        __props__.__dict__["endpoint_region"] = endpoint_region
        __props__.__dict__["interface"] = interface
        __props__.__dict__["name"] = name
        __props__.__dict__["region"] = region
        __props__.__dict__["service_id"] = service_id
        __props__.__dict__["service_name"] = service_name
        __props__.__dict__["service_type"] = service_type
        __props__.__dict__["url"] = url
        return EndpointV3(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="endpointRegion")
    def endpoint_region(self) -> pulumi.Output[str]:
        """
        The endpoint region. The `region` and
        `endpoint_region` can be different.
        """
        return pulumi.get(self, "endpoint_region")

    @property
    @pulumi.getter
    def interface(self) -> pulumi.Output[Optional[str]]:
        """
        The endpoint interface. Valid values are `public`,
        `internal` and `admin`. Default value is `public`
        """
        return pulumi.get(self, "interface")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The endpoint name.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def region(self) -> pulumi.Output[str]:
        """
        The region in which to obtain the V3 Keystone client.
        If omitted, the `region` argument of the provider is used.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter(name="serviceId")
    def service_id(self) -> pulumi.Output[str]:
        """
        The endpoint service ID.
        """
        return pulumi.get(self, "service_id")

    @property
    @pulumi.getter(name="serviceName")
    def service_name(self) -> pulumi.Output[str]:
        """
        The service name of the endpoint.
        """
        return pulumi.get(self, "service_name")

    @property
    @pulumi.getter(name="serviceType")
    def service_type(self) -> pulumi.Output[str]:
        """
        The service type of the endpoint.
        """
        return pulumi.get(self, "service_type")

    @property
    @pulumi.getter
    def url(self) -> pulumi.Output[str]:
        """
        The endpoint url.
        """
        return pulumi.get(self, "url")

