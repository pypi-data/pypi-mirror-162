# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['OrgSupportArgs', 'OrgSupport']

@pulumi.input_type
class OrgSupportArgs:
    def __init__(__self__, *,
                 extend_by: Optional[pulumi.Input[int]] = None):
        """
        The set of arguments for constructing a OrgSupport resource.
        :param pulumi.Input[int] extend_by: Number of days the support should be extended by in addition to the standard eight hours.
        """
        if extend_by is not None:
            pulumi.set(__self__, "extend_by", extend_by)

    @property
    @pulumi.getter(name="extendBy")
    def extend_by(self) -> Optional[pulumi.Input[int]]:
        """
        Number of days the support should be extended by in addition to the standard eight hours.
        """
        return pulumi.get(self, "extend_by")

    @extend_by.setter
    def extend_by(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "extend_by", value)


@pulumi.input_type
class _OrgSupportState:
    def __init__(__self__, *,
                 expiration: Optional[pulumi.Input[str]] = None,
                 extend_by: Optional[pulumi.Input[int]] = None,
                 status: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering OrgSupport resources.
        :param pulumi.Input[str] expiration: Expiration of Okta Support
        :param pulumi.Input[int] extend_by: Number of days the support should be extended by in addition to the standard eight hours.
        :param pulumi.Input[str] status: Status of Okta Support
        """
        if expiration is not None:
            pulumi.set(__self__, "expiration", expiration)
        if extend_by is not None:
            pulumi.set(__self__, "extend_by", extend_by)
        if status is not None:
            pulumi.set(__self__, "status", status)

    @property
    @pulumi.getter
    def expiration(self) -> Optional[pulumi.Input[str]]:
        """
        Expiration of Okta Support
        """
        return pulumi.get(self, "expiration")

    @expiration.setter
    def expiration(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "expiration", value)

    @property
    @pulumi.getter(name="extendBy")
    def extend_by(self) -> Optional[pulumi.Input[int]]:
        """
        Number of days the support should be extended by in addition to the standard eight hours.
        """
        return pulumi.get(self, "extend_by")

    @extend_by.setter
    def extend_by(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "extend_by", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input[str]]:
        """
        Status of Okta Support
        """
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "status", value)


class OrgSupport(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 extend_by: Optional[pulumi.Input[int]] = None,
                 __props__=None):
        """
        This resource allows you to temporarily allow Okta Support to access your org as an administrator. By default,
        access will be granted for eight hours. Removing this resource will revoke Okta Support access to your org.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_okta as okta

        example = okta.OrgSupport("example", extend_by=1)
        ```

        ## Import

        This resource does not support importing.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[int] extend_by: Number of days the support should be extended by in addition to the standard eight hours.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[OrgSupportArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        This resource allows you to temporarily allow Okta Support to access your org as an administrator. By default,
        access will be granted for eight hours. Removing this resource will revoke Okta Support access to your org.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_okta as okta

        example = okta.OrgSupport("example", extend_by=1)
        ```

        ## Import

        This resource does not support importing.

        :param str resource_name: The name of the resource.
        :param OrgSupportArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(OrgSupportArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 extend_by: Optional[pulumi.Input[int]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = OrgSupportArgs.__new__(OrgSupportArgs)

            __props__.__dict__["extend_by"] = extend_by
            __props__.__dict__["expiration"] = None
            __props__.__dict__["status"] = None
        super(OrgSupport, __self__).__init__(
            'okta:index/orgSupport:OrgSupport',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            expiration: Optional[pulumi.Input[str]] = None,
            extend_by: Optional[pulumi.Input[int]] = None,
            status: Optional[pulumi.Input[str]] = None) -> 'OrgSupport':
        """
        Get an existing OrgSupport resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] expiration: Expiration of Okta Support
        :param pulumi.Input[int] extend_by: Number of days the support should be extended by in addition to the standard eight hours.
        :param pulumi.Input[str] status: Status of Okta Support
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _OrgSupportState.__new__(_OrgSupportState)

        __props__.__dict__["expiration"] = expiration
        __props__.__dict__["extend_by"] = extend_by
        __props__.__dict__["status"] = status
        return OrgSupport(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def expiration(self) -> pulumi.Output[str]:
        """
        Expiration of Okta Support
        """
        return pulumi.get(self, "expiration")

    @property
    @pulumi.getter(name="extendBy")
    def extend_by(self) -> pulumi.Output[Optional[int]]:
        """
        Number of days the support should be extended by in addition to the standard eight hours.
        """
        return pulumi.get(self, "extend_by")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output[str]:
        """
        Status of Okta Support
        """
        return pulumi.get(self, "status")

