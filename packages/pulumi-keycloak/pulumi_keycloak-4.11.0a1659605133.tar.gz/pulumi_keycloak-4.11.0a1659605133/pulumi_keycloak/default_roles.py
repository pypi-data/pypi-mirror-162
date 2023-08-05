# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['DefaultRolesArgs', 'DefaultRoles']

@pulumi.input_type
class DefaultRolesArgs:
    def __init__(__self__, *,
                 default_roles: pulumi.Input[Sequence[pulumi.Input[str]]],
                 realm_id: pulumi.Input[str]):
        """
        The set of arguments for constructing a DefaultRoles resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] default_roles: Realm level roles assigned to new users by default.
        :param pulumi.Input[str] realm_id: The realm this role exists within.
        """
        pulumi.set(__self__, "default_roles", default_roles)
        pulumi.set(__self__, "realm_id", realm_id)

    @property
    @pulumi.getter(name="defaultRoles")
    def default_roles(self) -> pulumi.Input[Sequence[pulumi.Input[str]]]:
        """
        Realm level roles assigned to new users by default.
        """
        return pulumi.get(self, "default_roles")

    @default_roles.setter
    def default_roles(self, value: pulumi.Input[Sequence[pulumi.Input[str]]]):
        pulumi.set(self, "default_roles", value)

    @property
    @pulumi.getter(name="realmId")
    def realm_id(self) -> pulumi.Input[str]:
        """
        The realm this role exists within.
        """
        return pulumi.get(self, "realm_id")

    @realm_id.setter
    def realm_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "realm_id", value)


@pulumi.input_type
class _DefaultRolesState:
    def __init__(__self__, *,
                 default_roles: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 realm_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering DefaultRoles resources.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] default_roles: Realm level roles assigned to new users by default.
        :param pulumi.Input[str] realm_id: The realm this role exists within.
        """
        if default_roles is not None:
            pulumi.set(__self__, "default_roles", default_roles)
        if realm_id is not None:
            pulumi.set(__self__, "realm_id", realm_id)

    @property
    @pulumi.getter(name="defaultRoles")
    def default_roles(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Realm level roles assigned to new users by default.
        """
        return pulumi.get(self, "default_roles")

    @default_roles.setter
    def default_roles(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "default_roles", value)

    @property
    @pulumi.getter(name="realmId")
    def realm_id(self) -> Optional[pulumi.Input[str]]:
        """
        The realm this role exists within.
        """
        return pulumi.get(self, "realm_id")

    @realm_id.setter
    def realm_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "realm_id", value)


class DefaultRoles(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 default_roles: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 realm_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Allows managing default realm roles within Keycloak.

        Note: This feature was added in Keycloak v13, so this resource will not work on older versions of Keycloak.

        ## Example Usage
        ### Realm Role)

        ```python
        import pulumi
        import pulumi_keycloak as keycloak

        realm = keycloak.Realm("realm",
            realm="my-realm",
            enabled=True)
        default_roles = keycloak.DefaultRoles("defaultRoles",
            realm_id=realm.id,
            default_roles=["uma_authorization"])
        ```

        ## Import

        Default roles can be imported using the format `{{realm_id}}/{{default_role_id}}`, where `default_role_id` is the unique ID of the composite role that Keycloak uses to control default realm level roles. The ID is not easy to find in the GUI, but it appears in the dev tools when editing the default roles. Examplebash

        ```sh
         $ pulumi import keycloak:index/defaultRoles:DefaultRoles default_roles my-realm/a04c35c2-e95a-4dc5-bd32-e83a21be9e7d
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] default_roles: Realm level roles assigned to new users by default.
        :param pulumi.Input[str] realm_id: The realm this role exists within.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: DefaultRolesArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Allows managing default realm roles within Keycloak.

        Note: This feature was added in Keycloak v13, so this resource will not work on older versions of Keycloak.

        ## Example Usage
        ### Realm Role)

        ```python
        import pulumi
        import pulumi_keycloak as keycloak

        realm = keycloak.Realm("realm",
            realm="my-realm",
            enabled=True)
        default_roles = keycloak.DefaultRoles("defaultRoles",
            realm_id=realm.id,
            default_roles=["uma_authorization"])
        ```

        ## Import

        Default roles can be imported using the format `{{realm_id}}/{{default_role_id}}`, where `default_role_id` is the unique ID of the composite role that Keycloak uses to control default realm level roles. The ID is not easy to find in the GUI, but it appears in the dev tools when editing the default roles. Examplebash

        ```sh
         $ pulumi import keycloak:index/defaultRoles:DefaultRoles default_roles my-realm/a04c35c2-e95a-4dc5-bd32-e83a21be9e7d
        ```

        :param str resource_name: The name of the resource.
        :param DefaultRolesArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(DefaultRolesArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 default_roles: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 realm_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = DefaultRolesArgs.__new__(DefaultRolesArgs)

            if default_roles is None and not opts.urn:
                raise TypeError("Missing required property 'default_roles'")
            __props__.__dict__["default_roles"] = default_roles
            if realm_id is None and not opts.urn:
                raise TypeError("Missing required property 'realm_id'")
            __props__.__dict__["realm_id"] = realm_id
        super(DefaultRoles, __self__).__init__(
            'keycloak:index/defaultRoles:DefaultRoles',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            default_roles: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            realm_id: Optional[pulumi.Input[str]] = None) -> 'DefaultRoles':
        """
        Get an existing DefaultRoles resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] default_roles: Realm level roles assigned to new users by default.
        :param pulumi.Input[str] realm_id: The realm this role exists within.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _DefaultRolesState.__new__(_DefaultRolesState)

        __props__.__dict__["default_roles"] = default_roles
        __props__.__dict__["realm_id"] = realm_id
        return DefaultRoles(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="defaultRoles")
    def default_roles(self) -> pulumi.Output[Sequence[str]]:
        """
        Realm level roles assigned to new users by default.
        """
        return pulumi.get(self, "default_roles")

    @property
    @pulumi.getter(name="realmId")
    def realm_id(self) -> pulumi.Output[str]:
        """
        The realm this role exists within.
        """
        return pulumi.get(self, "realm_id")

