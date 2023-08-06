import dataclasses
import pathlib
import re
import typing

import yaml

from whocan import _errors
from whocan import _policies


PermissionDefiner = typing.Union[_policies.Policy, 'PolicySet']


@dataclasses.dataclass
class PolicySet:
    """A set of policies that interact to determine access."""

    policies: typing.List[PermissionDefiner]
    limit_policies: typing.List[PermissionDefiner]

    def is_allowed(
            self,
            action: str,
            resource: str = None,
            principal: str = None,
            arguments: typing.Dict[str, str] = None
    ) -> bool:
        """
        Determine if the given policy allows the specified action on the
        specified resource.

        :param action:
            The action being taken on the specified resource.
        :param resource:
            The resource on which the action is being taken.
        :param arguments:
            Arguments to pass into the policy before determining if
            access is allowed.
        :return:
            Whether the action is allowed on the resource.
        """
        return 'allow' == self.evaluate(action, resource, principal, arguments)

    def evaluate(
            self,
            action: str,
            resource: str = None,
            principal: str = None,
            arguments: typing.Dict[str, str] = None
    ) -> typing.Optional[str]:
        """
        Evaluate the policy to determine if it allows, denys, or makes no
        comment on the specified resource and action.

        :param action:
            The action being taken on the specified resource.
        :param resource:
            The resource on which the action is being taken.
        :param arguments:
            Arguments to pass into the policy before determining if
            access is allowed.
        :return:
            Either "allow", "deny" or None.
        """
        limited = _evaluate_policy_list(
            self.limit_policies,
            action,
            resource,
            principal,
            arguments,
            intersect=True
        )
        base = _evaluate_policy_list(
            self.policies, action, resource, principal, arguments
        )
        return limited if limited in {'deny', None} else base


def _evaluate_policy_list(
        policies: typing.List[PermissionDefiner],
        action: str,
        resource: str = None,
        principal: str = None,
        arguments: typing.Dict[str, str] = None,
        intersect: bool = False,
) -> typing.Optional[str]:
    """Evaluate a list of policies and policy sets."""
    evaluations = [
        policy.evaluate(action, resource, principal, arguments)
        for policy in policies
    ]
    if any(v == 'deny' for v in evaluations):
        return 'deny'
    handler = all if intersect else any
    if handler(v == 'allow' for v in evaluations):
        return 'allow'
    return None
