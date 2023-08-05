# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['RulePasswordArgs', 'RulePassword']

@pulumi.input_type
class RulePasswordArgs:
    def __init__(__self__, *,
                 name: Optional[pulumi.Input[str]] = None,
                 network_connection: Optional[pulumi.Input[str]] = None,
                 network_excludes: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 network_includes: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 password_change: Optional[pulumi.Input[str]] = None,
                 password_reset: Optional[pulumi.Input[str]] = None,
                 password_unlock: Optional[pulumi.Input[str]] = None,
                 policy_id: Optional[pulumi.Input[str]] = None,
                 policyid: Optional[pulumi.Input[str]] = None,
                 priority: Optional[pulumi.Input[int]] = None,
                 status: Optional[pulumi.Input[str]] = None,
                 users_excludeds: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a RulePassword resource.
        :param pulumi.Input[str] name: Policy Rule Name.
        :param pulumi.Input[str] network_connection: Network selection mode: `"ANYWHERE"`, `"ZONE"`, `"ON_NETWORK"`, or `"OFF_NETWORK"`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] network_excludes: The network zones to exclude. Conflicts with `network_includes`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] network_includes: The network zones to include. Conflicts with `network_excludes`.
        :param pulumi.Input[str] password_change: Allow or deny a user to change their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        :param pulumi.Input[str] password_reset: Allow or deny a user to reset their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        :param pulumi.Input[str] password_unlock: Allow or deny a user to unlock: `"ALLOW"` or `"DENY"`. By default, it is `"DENY"`,
        :param pulumi.Input[str] policy_id: Policy ID.
        :param pulumi.Input[str] policyid: Policy ID.
        :param pulumi.Input[int] priority: Policy Rule Priority, this attribute can be set to a valid priority. To avoid endless diff situation we error if an invalid priority is provided. API defaults it to the last (lowest) if not there.
        :param pulumi.Input[str] status: Policy Rule Status: `"ACTIVE"` or `"INACTIVE"`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] users_excludeds: Set of User IDs to Exclude
        """
        if name is not None:
            pulumi.set(__self__, "name", name)
        if network_connection is not None:
            pulumi.set(__self__, "network_connection", network_connection)
        if network_excludes is not None:
            pulumi.set(__self__, "network_excludes", network_excludes)
        if network_includes is not None:
            pulumi.set(__self__, "network_includes", network_includes)
        if password_change is not None:
            pulumi.set(__self__, "password_change", password_change)
        if password_reset is not None:
            pulumi.set(__self__, "password_reset", password_reset)
        if password_unlock is not None:
            pulumi.set(__self__, "password_unlock", password_unlock)
        if policy_id is not None:
            pulumi.set(__self__, "policy_id", policy_id)
        if policyid is not None:
            warnings.warn("""Because of incorrect naming, 'policyid' field will be deprecated and then removed in the next versions of the provider. Please use 'policy_id' instead""", DeprecationWarning)
            pulumi.log.warn("""policyid is deprecated: Because of incorrect naming, 'policyid' field will be deprecated and then removed in the next versions of the provider. Please use 'policy_id' instead""")
        if policyid is not None:
            pulumi.set(__self__, "policyid", policyid)
        if priority is not None:
            pulumi.set(__self__, "priority", priority)
        if status is not None:
            pulumi.set(__self__, "status", status)
        if users_excludeds is not None:
            pulumi.set(__self__, "users_excludeds", users_excludeds)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Policy Rule Name.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="networkConnection")
    def network_connection(self) -> Optional[pulumi.Input[str]]:
        """
        Network selection mode: `"ANYWHERE"`, `"ZONE"`, `"ON_NETWORK"`, or `"OFF_NETWORK"`.
        """
        return pulumi.get(self, "network_connection")

    @network_connection.setter
    def network_connection(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "network_connection", value)

    @property
    @pulumi.getter(name="networkExcludes")
    def network_excludes(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The network zones to exclude. Conflicts with `network_includes`.
        """
        return pulumi.get(self, "network_excludes")

    @network_excludes.setter
    def network_excludes(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "network_excludes", value)

    @property
    @pulumi.getter(name="networkIncludes")
    def network_includes(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The network zones to include. Conflicts with `network_excludes`.
        """
        return pulumi.get(self, "network_includes")

    @network_includes.setter
    def network_includes(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "network_includes", value)

    @property
    @pulumi.getter(name="passwordChange")
    def password_change(self) -> Optional[pulumi.Input[str]]:
        """
        Allow or deny a user to change their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        """
        return pulumi.get(self, "password_change")

    @password_change.setter
    def password_change(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "password_change", value)

    @property
    @pulumi.getter(name="passwordReset")
    def password_reset(self) -> Optional[pulumi.Input[str]]:
        """
        Allow or deny a user to reset their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        """
        return pulumi.get(self, "password_reset")

    @password_reset.setter
    def password_reset(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "password_reset", value)

    @property
    @pulumi.getter(name="passwordUnlock")
    def password_unlock(self) -> Optional[pulumi.Input[str]]:
        """
        Allow or deny a user to unlock: `"ALLOW"` or `"DENY"`. By default, it is `"DENY"`,
        """
        return pulumi.get(self, "password_unlock")

    @password_unlock.setter
    def password_unlock(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "password_unlock", value)

    @property
    @pulumi.getter(name="policyId")
    def policy_id(self) -> Optional[pulumi.Input[str]]:
        """
        Policy ID.
        """
        return pulumi.get(self, "policy_id")

    @policy_id.setter
    def policy_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy_id", value)

    @property
    @pulumi.getter
    def policyid(self) -> Optional[pulumi.Input[str]]:
        """
        Policy ID.
        """
        return pulumi.get(self, "policyid")

    @policyid.setter
    def policyid(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policyid", value)

    @property
    @pulumi.getter
    def priority(self) -> Optional[pulumi.Input[int]]:
        """
        Policy Rule Priority, this attribute can be set to a valid priority. To avoid endless diff situation we error if an invalid priority is provided. API defaults it to the last (lowest) if not there.
        """
        return pulumi.get(self, "priority")

    @priority.setter
    def priority(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "priority", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input[str]]:
        """
        Policy Rule Status: `"ACTIVE"` or `"INACTIVE"`.
        """
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "status", value)

    @property
    @pulumi.getter(name="usersExcludeds")
    def users_excludeds(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Set of User IDs to Exclude
        """
        return pulumi.get(self, "users_excludeds")

    @users_excludeds.setter
    def users_excludeds(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "users_excludeds", value)


@pulumi.input_type
class _RulePasswordState:
    def __init__(__self__, *,
                 name: Optional[pulumi.Input[str]] = None,
                 network_connection: Optional[pulumi.Input[str]] = None,
                 network_excludes: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 network_includes: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 password_change: Optional[pulumi.Input[str]] = None,
                 password_reset: Optional[pulumi.Input[str]] = None,
                 password_unlock: Optional[pulumi.Input[str]] = None,
                 policy_id: Optional[pulumi.Input[str]] = None,
                 policyid: Optional[pulumi.Input[str]] = None,
                 priority: Optional[pulumi.Input[int]] = None,
                 status: Optional[pulumi.Input[str]] = None,
                 users_excludeds: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering RulePassword resources.
        :param pulumi.Input[str] name: Policy Rule Name.
        :param pulumi.Input[str] network_connection: Network selection mode: `"ANYWHERE"`, `"ZONE"`, `"ON_NETWORK"`, or `"OFF_NETWORK"`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] network_excludes: The network zones to exclude. Conflicts with `network_includes`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] network_includes: The network zones to include. Conflicts with `network_excludes`.
        :param pulumi.Input[str] password_change: Allow or deny a user to change their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        :param pulumi.Input[str] password_reset: Allow or deny a user to reset their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        :param pulumi.Input[str] password_unlock: Allow or deny a user to unlock: `"ALLOW"` or `"DENY"`. By default, it is `"DENY"`,
        :param pulumi.Input[str] policy_id: Policy ID.
        :param pulumi.Input[str] policyid: Policy ID.
        :param pulumi.Input[int] priority: Policy Rule Priority, this attribute can be set to a valid priority. To avoid endless diff situation we error if an invalid priority is provided. API defaults it to the last (lowest) if not there.
        :param pulumi.Input[str] status: Policy Rule Status: `"ACTIVE"` or `"INACTIVE"`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] users_excludeds: Set of User IDs to Exclude
        """
        if name is not None:
            pulumi.set(__self__, "name", name)
        if network_connection is not None:
            pulumi.set(__self__, "network_connection", network_connection)
        if network_excludes is not None:
            pulumi.set(__self__, "network_excludes", network_excludes)
        if network_includes is not None:
            pulumi.set(__self__, "network_includes", network_includes)
        if password_change is not None:
            pulumi.set(__self__, "password_change", password_change)
        if password_reset is not None:
            pulumi.set(__self__, "password_reset", password_reset)
        if password_unlock is not None:
            pulumi.set(__self__, "password_unlock", password_unlock)
        if policy_id is not None:
            pulumi.set(__self__, "policy_id", policy_id)
        if policyid is not None:
            warnings.warn("""Because of incorrect naming, 'policyid' field will be deprecated and then removed in the next versions of the provider. Please use 'policy_id' instead""", DeprecationWarning)
            pulumi.log.warn("""policyid is deprecated: Because of incorrect naming, 'policyid' field will be deprecated and then removed in the next versions of the provider. Please use 'policy_id' instead""")
        if policyid is not None:
            pulumi.set(__self__, "policyid", policyid)
        if priority is not None:
            pulumi.set(__self__, "priority", priority)
        if status is not None:
            pulumi.set(__self__, "status", status)
        if users_excludeds is not None:
            pulumi.set(__self__, "users_excludeds", users_excludeds)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Policy Rule Name.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="networkConnection")
    def network_connection(self) -> Optional[pulumi.Input[str]]:
        """
        Network selection mode: `"ANYWHERE"`, `"ZONE"`, `"ON_NETWORK"`, or `"OFF_NETWORK"`.
        """
        return pulumi.get(self, "network_connection")

    @network_connection.setter
    def network_connection(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "network_connection", value)

    @property
    @pulumi.getter(name="networkExcludes")
    def network_excludes(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The network zones to exclude. Conflicts with `network_includes`.
        """
        return pulumi.get(self, "network_excludes")

    @network_excludes.setter
    def network_excludes(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "network_excludes", value)

    @property
    @pulumi.getter(name="networkIncludes")
    def network_includes(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The network zones to include. Conflicts with `network_excludes`.
        """
        return pulumi.get(self, "network_includes")

    @network_includes.setter
    def network_includes(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "network_includes", value)

    @property
    @pulumi.getter(name="passwordChange")
    def password_change(self) -> Optional[pulumi.Input[str]]:
        """
        Allow or deny a user to change their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        """
        return pulumi.get(self, "password_change")

    @password_change.setter
    def password_change(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "password_change", value)

    @property
    @pulumi.getter(name="passwordReset")
    def password_reset(self) -> Optional[pulumi.Input[str]]:
        """
        Allow or deny a user to reset their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        """
        return pulumi.get(self, "password_reset")

    @password_reset.setter
    def password_reset(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "password_reset", value)

    @property
    @pulumi.getter(name="passwordUnlock")
    def password_unlock(self) -> Optional[pulumi.Input[str]]:
        """
        Allow or deny a user to unlock: `"ALLOW"` or `"DENY"`. By default, it is `"DENY"`,
        """
        return pulumi.get(self, "password_unlock")

    @password_unlock.setter
    def password_unlock(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "password_unlock", value)

    @property
    @pulumi.getter(name="policyId")
    def policy_id(self) -> Optional[pulumi.Input[str]]:
        """
        Policy ID.
        """
        return pulumi.get(self, "policy_id")

    @policy_id.setter
    def policy_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy_id", value)

    @property
    @pulumi.getter
    def policyid(self) -> Optional[pulumi.Input[str]]:
        """
        Policy ID.
        """
        return pulumi.get(self, "policyid")

    @policyid.setter
    def policyid(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policyid", value)

    @property
    @pulumi.getter
    def priority(self) -> Optional[pulumi.Input[int]]:
        """
        Policy Rule Priority, this attribute can be set to a valid priority. To avoid endless diff situation we error if an invalid priority is provided. API defaults it to the last (lowest) if not there.
        """
        return pulumi.get(self, "priority")

    @priority.setter
    def priority(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "priority", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input[str]]:
        """
        Policy Rule Status: `"ACTIVE"` or `"INACTIVE"`.
        """
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "status", value)

    @property
    @pulumi.getter(name="usersExcludeds")
    def users_excludeds(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Set of User IDs to Exclude
        """
        return pulumi.get(self, "users_excludeds")

    @users_excludeds.setter
    def users_excludeds(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "users_excludeds", value)


class RulePassword(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 network_connection: Optional[pulumi.Input[str]] = None,
                 network_excludes: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 network_includes: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 password_change: Optional[pulumi.Input[str]] = None,
                 password_reset: Optional[pulumi.Input[str]] = None,
                 password_unlock: Optional[pulumi.Input[str]] = None,
                 policy_id: Optional[pulumi.Input[str]] = None,
                 policyid: Optional[pulumi.Input[str]] = None,
                 priority: Optional[pulumi.Input[int]] = None,
                 status: Optional[pulumi.Input[str]] = None,
                 users_excludeds: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Creates a Password Policy Rule.

        This resource allows you to create and configure a Password Policy Rule.

        ## Import

        A Policy Rule can be imported via the Policy and Rule ID.

        ```sh
         $ pulumi import okta:policy/rulePassword:RulePassword example &#60;policy id&#62;/&#60;rule id&#62;
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] name: Policy Rule Name.
        :param pulumi.Input[str] network_connection: Network selection mode: `"ANYWHERE"`, `"ZONE"`, `"ON_NETWORK"`, or `"OFF_NETWORK"`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] network_excludes: The network zones to exclude. Conflicts with `network_includes`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] network_includes: The network zones to include. Conflicts with `network_excludes`.
        :param pulumi.Input[str] password_change: Allow or deny a user to change their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        :param pulumi.Input[str] password_reset: Allow or deny a user to reset their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        :param pulumi.Input[str] password_unlock: Allow or deny a user to unlock: `"ALLOW"` or `"DENY"`. By default, it is `"DENY"`,
        :param pulumi.Input[str] policy_id: Policy ID.
        :param pulumi.Input[str] policyid: Policy ID.
        :param pulumi.Input[int] priority: Policy Rule Priority, this attribute can be set to a valid priority. To avoid endless diff situation we error if an invalid priority is provided. API defaults it to the last (lowest) if not there.
        :param pulumi.Input[str] status: Policy Rule Status: `"ACTIVE"` or `"INACTIVE"`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] users_excludeds: Set of User IDs to Exclude
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[RulePasswordArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a Password Policy Rule.

        This resource allows you to create and configure a Password Policy Rule.

        ## Import

        A Policy Rule can be imported via the Policy and Rule ID.

        ```sh
         $ pulumi import okta:policy/rulePassword:RulePassword example &#60;policy id&#62;/&#60;rule id&#62;
        ```

        :param str resource_name: The name of the resource.
        :param RulePasswordArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(RulePasswordArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 network_connection: Optional[pulumi.Input[str]] = None,
                 network_excludes: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 network_includes: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 password_change: Optional[pulumi.Input[str]] = None,
                 password_reset: Optional[pulumi.Input[str]] = None,
                 password_unlock: Optional[pulumi.Input[str]] = None,
                 policy_id: Optional[pulumi.Input[str]] = None,
                 policyid: Optional[pulumi.Input[str]] = None,
                 priority: Optional[pulumi.Input[int]] = None,
                 status: Optional[pulumi.Input[str]] = None,
                 users_excludeds: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = RulePasswordArgs.__new__(RulePasswordArgs)

            __props__.__dict__["name"] = name
            __props__.__dict__["network_connection"] = network_connection
            __props__.__dict__["network_excludes"] = network_excludes
            __props__.__dict__["network_includes"] = network_includes
            __props__.__dict__["password_change"] = password_change
            __props__.__dict__["password_reset"] = password_reset
            __props__.__dict__["password_unlock"] = password_unlock
            __props__.__dict__["policy_id"] = policy_id
            if policyid is not None and not opts.urn:
                warnings.warn("""Because of incorrect naming, 'policyid' field will be deprecated and then removed in the next versions of the provider. Please use 'policy_id' instead""", DeprecationWarning)
                pulumi.log.warn("""policyid is deprecated: Because of incorrect naming, 'policyid' field will be deprecated and then removed in the next versions of the provider. Please use 'policy_id' instead""")
            __props__.__dict__["policyid"] = policyid
            __props__.__dict__["priority"] = priority
            __props__.__dict__["status"] = status
            __props__.__dict__["users_excludeds"] = users_excludeds
        super(RulePassword, __self__).__init__(
            'okta:policy/rulePassword:RulePassword',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            name: Optional[pulumi.Input[str]] = None,
            network_connection: Optional[pulumi.Input[str]] = None,
            network_excludes: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            network_includes: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            password_change: Optional[pulumi.Input[str]] = None,
            password_reset: Optional[pulumi.Input[str]] = None,
            password_unlock: Optional[pulumi.Input[str]] = None,
            policy_id: Optional[pulumi.Input[str]] = None,
            policyid: Optional[pulumi.Input[str]] = None,
            priority: Optional[pulumi.Input[int]] = None,
            status: Optional[pulumi.Input[str]] = None,
            users_excludeds: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None) -> 'RulePassword':
        """
        Get an existing RulePassword resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] name: Policy Rule Name.
        :param pulumi.Input[str] network_connection: Network selection mode: `"ANYWHERE"`, `"ZONE"`, `"ON_NETWORK"`, or `"OFF_NETWORK"`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] network_excludes: The network zones to exclude. Conflicts with `network_includes`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] network_includes: The network zones to include. Conflicts with `network_excludes`.
        :param pulumi.Input[str] password_change: Allow or deny a user to change their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        :param pulumi.Input[str] password_reset: Allow or deny a user to reset their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        :param pulumi.Input[str] password_unlock: Allow or deny a user to unlock: `"ALLOW"` or `"DENY"`. By default, it is `"DENY"`,
        :param pulumi.Input[str] policy_id: Policy ID.
        :param pulumi.Input[str] policyid: Policy ID.
        :param pulumi.Input[int] priority: Policy Rule Priority, this attribute can be set to a valid priority. To avoid endless diff situation we error if an invalid priority is provided. API defaults it to the last (lowest) if not there.
        :param pulumi.Input[str] status: Policy Rule Status: `"ACTIVE"` or `"INACTIVE"`.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] users_excludeds: Set of User IDs to Exclude
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _RulePasswordState.__new__(_RulePasswordState)

        __props__.__dict__["name"] = name
        __props__.__dict__["network_connection"] = network_connection
        __props__.__dict__["network_excludes"] = network_excludes
        __props__.__dict__["network_includes"] = network_includes
        __props__.__dict__["password_change"] = password_change
        __props__.__dict__["password_reset"] = password_reset
        __props__.__dict__["password_unlock"] = password_unlock
        __props__.__dict__["policy_id"] = policy_id
        __props__.__dict__["policyid"] = policyid
        __props__.__dict__["priority"] = priority
        __props__.__dict__["status"] = status
        __props__.__dict__["users_excludeds"] = users_excludeds
        return RulePassword(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Policy Rule Name.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="networkConnection")
    def network_connection(self) -> pulumi.Output[Optional[str]]:
        """
        Network selection mode: `"ANYWHERE"`, `"ZONE"`, `"ON_NETWORK"`, or `"OFF_NETWORK"`.
        """
        return pulumi.get(self, "network_connection")

    @property
    @pulumi.getter(name="networkExcludes")
    def network_excludes(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        The network zones to exclude. Conflicts with `network_includes`.
        """
        return pulumi.get(self, "network_excludes")

    @property
    @pulumi.getter(name="networkIncludes")
    def network_includes(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        The network zones to include. Conflicts with `network_excludes`.
        """
        return pulumi.get(self, "network_includes")

    @property
    @pulumi.getter(name="passwordChange")
    def password_change(self) -> pulumi.Output[Optional[str]]:
        """
        Allow or deny a user to change their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        """
        return pulumi.get(self, "password_change")

    @property
    @pulumi.getter(name="passwordReset")
    def password_reset(self) -> pulumi.Output[Optional[str]]:
        """
        Allow or deny a user to reset their password: `"ALLOW"` or `"DENY"`. By default, it is `"ALLOW"`.
        """
        return pulumi.get(self, "password_reset")

    @property
    @pulumi.getter(name="passwordUnlock")
    def password_unlock(self) -> pulumi.Output[Optional[str]]:
        """
        Allow or deny a user to unlock: `"ALLOW"` or `"DENY"`. By default, it is `"DENY"`,
        """
        return pulumi.get(self, "password_unlock")

    @property
    @pulumi.getter(name="policyId")
    def policy_id(self) -> pulumi.Output[Optional[str]]:
        """
        Policy ID.
        """
        return pulumi.get(self, "policy_id")

    @property
    @pulumi.getter
    def policyid(self) -> pulumi.Output[Optional[str]]:
        """
        Policy ID.
        """
        return pulumi.get(self, "policyid")

    @property
    @pulumi.getter
    def priority(self) -> pulumi.Output[Optional[int]]:
        """
        Policy Rule Priority, this attribute can be set to a valid priority. To avoid endless diff situation we error if an invalid priority is provided. API defaults it to the last (lowest) if not there.
        """
        return pulumi.get(self, "priority")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output[Optional[str]]:
        """
        Policy Rule Status: `"ACTIVE"` or `"INACTIVE"`.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter(name="usersExcludeds")
    def users_excludeds(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        Set of User IDs to Exclude
        """
        return pulumi.get(self, "users_excludeds")

