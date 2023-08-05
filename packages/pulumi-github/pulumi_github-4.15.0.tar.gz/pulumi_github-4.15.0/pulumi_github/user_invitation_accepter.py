# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['UserInvitationAccepterArgs', 'UserInvitationAccepter']

@pulumi.input_type
class UserInvitationAccepterArgs:
    def __init__(__self__, *,
                 invitation_id: pulumi.Input[str]):
        """
        The set of arguments for constructing a UserInvitationAccepter resource.
        :param pulumi.Input[str] invitation_id: ID of the invitation to accept
        """
        pulumi.set(__self__, "invitation_id", invitation_id)

    @property
    @pulumi.getter(name="invitationId")
    def invitation_id(self) -> pulumi.Input[str]:
        """
        ID of the invitation to accept
        """
        return pulumi.get(self, "invitation_id")

    @invitation_id.setter
    def invitation_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "invitation_id", value)


@pulumi.input_type
class _UserInvitationAccepterState:
    def __init__(__self__, *,
                 invitation_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering UserInvitationAccepter resources.
        :param pulumi.Input[str] invitation_id: ID of the invitation to accept
        """
        if invitation_id is not None:
            pulumi.set(__self__, "invitation_id", invitation_id)

    @property
    @pulumi.getter(name="invitationId")
    def invitation_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the invitation to accept
        """
        return pulumi.get(self, "invitation_id")

    @invitation_id.setter
    def invitation_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "invitation_id", value)


class UserInvitationAccepter(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 invitation_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides a resource to manage GitHub repository collaborator invitations.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_github as github
        import pulumi_pulumi as pulumi

        example_repository = github.Repository("exampleRepository")
        example_repository_collaborator = github.RepositoryCollaborator("exampleRepositoryCollaborator",
            repository=example_repository.name,
            username="example-username",
            permission="push")
        invitee = pulumi.providers.Github("invitee", token=var["invitee_token"])
        example_user_invitation_accepter = github.UserInvitationAccepter("exampleUserInvitationAccepter", invitation_id=example_repository_collaborator.invitation_id,
        opts=pulumi.ResourceOptions(provider="github.invitee"))
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] invitation_id: ID of the invitation to accept
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: UserInvitationAccepterArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a resource to manage GitHub repository collaborator invitations.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_github as github
        import pulumi_pulumi as pulumi

        example_repository = github.Repository("exampleRepository")
        example_repository_collaborator = github.RepositoryCollaborator("exampleRepositoryCollaborator",
            repository=example_repository.name,
            username="example-username",
            permission="push")
        invitee = pulumi.providers.Github("invitee", token=var["invitee_token"])
        example_user_invitation_accepter = github.UserInvitationAccepter("exampleUserInvitationAccepter", invitation_id=example_repository_collaborator.invitation_id,
        opts=pulumi.ResourceOptions(provider="github.invitee"))
        ```

        :param str resource_name: The name of the resource.
        :param UserInvitationAccepterArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(UserInvitationAccepterArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 invitation_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = UserInvitationAccepterArgs.__new__(UserInvitationAccepterArgs)

            if invitation_id is None and not opts.urn:
                raise TypeError("Missing required property 'invitation_id'")
            __props__.__dict__["invitation_id"] = invitation_id
        super(UserInvitationAccepter, __self__).__init__(
            'github:index/userInvitationAccepter:UserInvitationAccepter',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            invitation_id: Optional[pulumi.Input[str]] = None) -> 'UserInvitationAccepter':
        """
        Get an existing UserInvitationAccepter resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] invitation_id: ID of the invitation to accept
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _UserInvitationAccepterState.__new__(_UserInvitationAccepterState)

        __props__.__dict__["invitation_id"] = invitation_id
        return UserInvitationAccepter(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="invitationId")
    def invitation_id(self) -> pulumi.Output[str]:
        """
        ID of the invitation to accept
        """
        return pulumi.get(self, "invitation_id")

