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

__all__ = ['TeamMembersArgs', 'TeamMembers']

@pulumi.input_type
class TeamMembersArgs:
    def __init__(__self__, *,
                 members: pulumi.Input[Sequence[pulumi.Input['TeamMembersMemberArgs']]],
                 team_id: pulumi.Input[str]):
        """
        The set of arguments for constructing a TeamMembers resource.
        :param pulumi.Input[Sequence[pulumi.Input['TeamMembersMemberArgs']]] members: List of team members. See Members below for details.
        :param pulumi.Input[str] team_id: The GitHub team id
        """
        pulumi.set(__self__, "members", members)
        pulumi.set(__self__, "team_id", team_id)

    @property
    @pulumi.getter
    def members(self) -> pulumi.Input[Sequence[pulumi.Input['TeamMembersMemberArgs']]]:
        """
        List of team members. See Members below for details.
        """
        return pulumi.get(self, "members")

    @members.setter
    def members(self, value: pulumi.Input[Sequence[pulumi.Input['TeamMembersMemberArgs']]]):
        pulumi.set(self, "members", value)

    @property
    @pulumi.getter(name="teamId")
    def team_id(self) -> pulumi.Input[str]:
        """
        The GitHub team id
        """
        return pulumi.get(self, "team_id")

    @team_id.setter
    def team_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "team_id", value)


@pulumi.input_type
class _TeamMembersState:
    def __init__(__self__, *,
                 etag: Optional[pulumi.Input[str]] = None,
                 members: Optional[pulumi.Input[Sequence[pulumi.Input['TeamMembersMemberArgs']]]] = None,
                 team_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering TeamMembers resources.
        :param pulumi.Input[Sequence[pulumi.Input['TeamMembersMemberArgs']]] members: List of team members. See Members below for details.
        :param pulumi.Input[str] team_id: The GitHub team id
        """
        if etag is not None:
            pulumi.set(__self__, "etag", etag)
        if members is not None:
            pulumi.set(__self__, "members", members)
        if team_id is not None:
            pulumi.set(__self__, "team_id", team_id)

    @property
    @pulumi.getter
    def etag(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "etag")

    @etag.setter
    def etag(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "etag", value)

    @property
    @pulumi.getter
    def members(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['TeamMembersMemberArgs']]]]:
        """
        List of team members. See Members below for details.
        """
        return pulumi.get(self, "members")

    @members.setter
    def members(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['TeamMembersMemberArgs']]]]):
        pulumi.set(self, "members", value)

    @property
    @pulumi.getter(name="teamId")
    def team_id(self) -> Optional[pulumi.Input[str]]:
        """
        The GitHub team id
        """
        return pulumi.get(self, "team_id")

    @team_id.setter
    def team_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "team_id", value)


class TeamMembers(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['TeamMembersMemberArgs']]]]] = None,
                 team_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        ## Example Usage

        ```python
        import pulumi
        import pulumi_github as github

        # Add a user to the organization
        membership_for_some_user = github.Membership("membershipForSomeUser",
            username="SomeUser",
            role="member")
        membership_for_another_user = github.Membership("membershipForAnotherUser",
            username="AnotherUser",
            role="member")
        some_team = github.Team("someTeam", description="Some cool team")
        some_team_members = github.TeamMembers("someTeamMembers",
            team_id=some_team.id,
            members=[
                github.TeamMembersMemberArgs(
                    username="SomeUser",
                    role="maintainer",
                ),
                github.TeamMembersMemberArgs(
                    username="AnotherUser",
                    role="member",
                ),
            ])
        ```

        ## Import

        GitHub Team Membership can be imported using the team ID `teamid`, e.g.

        ```sh
         $ pulumi import github:index/teamMembers:TeamMembers some_team 1234567
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['TeamMembersMemberArgs']]]] members: List of team members. See Members below for details.
        :param pulumi.Input[str] team_id: The GitHub team id
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: TeamMembersArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        ## Example Usage

        ```python
        import pulumi
        import pulumi_github as github

        # Add a user to the organization
        membership_for_some_user = github.Membership("membershipForSomeUser",
            username="SomeUser",
            role="member")
        membership_for_another_user = github.Membership("membershipForAnotherUser",
            username="AnotherUser",
            role="member")
        some_team = github.Team("someTeam", description="Some cool team")
        some_team_members = github.TeamMembers("someTeamMembers",
            team_id=some_team.id,
            members=[
                github.TeamMembersMemberArgs(
                    username="SomeUser",
                    role="maintainer",
                ),
                github.TeamMembersMemberArgs(
                    username="AnotherUser",
                    role="member",
                ),
            ])
        ```

        ## Import

        GitHub Team Membership can be imported using the team ID `teamid`, e.g.

        ```sh
         $ pulumi import github:index/teamMembers:TeamMembers some_team 1234567
        ```

        :param str resource_name: The name of the resource.
        :param TeamMembersArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(TeamMembersArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['TeamMembersMemberArgs']]]]] = None,
                 team_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = TeamMembersArgs.__new__(TeamMembersArgs)

            if members is None and not opts.urn:
                raise TypeError("Missing required property 'members'")
            __props__.__dict__["members"] = members
            if team_id is None and not opts.urn:
                raise TypeError("Missing required property 'team_id'")
            __props__.__dict__["team_id"] = team_id
            __props__.__dict__["etag"] = None
        super(TeamMembers, __self__).__init__(
            'github:index/teamMembers:TeamMembers',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            etag: Optional[pulumi.Input[str]] = None,
            members: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['TeamMembersMemberArgs']]]]] = None,
            team_id: Optional[pulumi.Input[str]] = None) -> 'TeamMembers':
        """
        Get an existing TeamMembers resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['TeamMembersMemberArgs']]]] members: List of team members. See Members below for details.
        :param pulumi.Input[str] team_id: The GitHub team id
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _TeamMembersState.__new__(_TeamMembersState)

        __props__.__dict__["etag"] = etag
        __props__.__dict__["members"] = members
        __props__.__dict__["team_id"] = team_id
        return TeamMembers(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def etag(self) -> pulumi.Output[str]:
        return pulumi.get(self, "etag")

    @property
    @pulumi.getter
    def members(self) -> pulumi.Output[Sequence['outputs.TeamMembersMember']]:
        """
        List of team members. See Members below for details.
        """
        return pulumi.get(self, "members")

    @property
    @pulumi.getter(name="teamId")
    def team_id(self) -> pulumi.Output[str]:
        """
        The GitHub team id
        """
        return pulumi.get(self, "team_id")

