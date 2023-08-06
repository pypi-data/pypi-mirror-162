import dataclasses
import pathlib
import re
import typing

import yaml

from whocan import _errors


def _force_to_list(
        value: typing.Union[typing.List[str], str]
) -> typing.List[str]:
    """Force the value to a list."""
    if isinstance(value, str):
        return [value]
    return value


def _policy_check(raise_issue: bool, message: str):
    """Raise the error if raise_issue is true."""
    if raise_issue:
        raise _errors.PolicyYamlInvalidError(message)


def _validate_yaml(raw_yaml: typing.Any):
    """Validate the yaml or raise an error if it is invalid."""
    if not isinstance(raw_yaml, dict):
        raise _errors.PolicyYamlInvalidError(
            'Top level of policy must be a dictionary.'
        )
    _policy_check(
        'statements' not in raw_yaml,
        'Missing required field "statements".'
    )
    _policy_check(
        not isinstance(raw_yaml['statements'], list),
        '"statements" must be a list.'
    )

    for i, statement in enumerate(raw_yaml['statements']):
        required = ['effect', 'actions']
        for r in required:
            _policy_check(
                r not in statement,
                f'Missing required field "statements[{i}].{r}".'
            )
        _policy_check(
            not ('principals' in statement or 'resources' in statement),
            (
                f'Missing required field in "statements[{i}]". Must include '
                'either "resources" or "principals".'
            )
        )
        _policy_check(
            statement['effect'] not in {'allow', 'deny'},
            f'Missing required field "statements[{i}].effect"'
            ' must be "allow" or "deny".'
        )
        _policy_check(
            (
                'resources' in statement
                and not isinstance(statement['resources'], (str, list))
            ),
            f'"statements[{i}].resources" must be a string or list.'
        )
        _policy_check(
            (
                'principals' in statement
                and not isinstance(statement['principals'], (str, list))
            ),
            f'"statements[{i}].principals" must be a string or list.'
        )
        _policy_check(
            not isinstance(statement['actions'], (str, list)),
            f'Missing required field "statements[{i}].actions"'
            ' must be a string or list.'
        )
        key = 'resources'
        if key in statement and isinstance(statement[key], list):
            _policy_check(
                any(not isinstance(r, str) for r in statement['resources']),
                f'All members of "statements[{i}].resources" must be strings.'
            )
        key = 'principals'
        if key in statement and isinstance(statement[key], list):
            _policy_check(
                any(not isinstance(r, str) for r in statement['principals']),
                f'All members of "statements[{i}].principals" must be strings.'
            )
        if isinstance(statement['actions'], list):
            _policy_check(
                any(not isinstance(a, str) for a in statement['actions']),
                f'All members of "statements[{i}].actions" must be strings.'
            )


def _form_regex(
        base: str,
        arguments: typing.Dict[str, str],
        strict: bool,
) -> str:
    """Form a regex from the given base value and arguments."""
    previous = 0
    processed = []
    for m in re.finditer(r'(\*+)', base):
        if m.start() != previous:
            processed.append(re.escape(base[previous:m.start()]))
        if m.group(1) == '*':
            processed.append('[^/]*')
        if m.group(1).startswith('**'):
            processed.append('.*')
        previous = m.end()
    processed.append(re.escape(base[previous:]))
    pattern = ''.join(processed)
    return f'^{pattern}$'


@dataclasses.dataclass
class Line:
    """A single resource or action."""

    raw_line: str
    arguments: typing.Dict[str, str]
    strict: bool = True

    def is_match(self, value: str) -> bool:
        """Determine if the given value is a match for the line."""
        if self.line == '*':
            return True
        values = value.split(':')
        pieces = self.line.split(':')
        if len(values) != len(pieces):
            return False
        for piece, incoming in zip(pieces, values):
            pattern = _form_regex(piece, self.arguments, self.strict)
            if not re.fullmatch(pattern, incoming):
                return False
        return True

    @property
    def line(self) -> str:
        """Get the line with arguments rendered in."""
        previous = 0
        processed = []
        for m in re.finditer(r'((?:\${\s*(\w+)\s*}))', self.raw_line):
            if m.start() != previous:
                processed.append(self.raw_line[previous:m.start()])
            if m.group(2):
                parameter = m.group(2)
                if parameter not in self.arguments and self.strict:
                    raise _errors.PolicyEvaluationError(
                        f'"{parameter}" unknown variable.'
                    )
                processed.append(str(self.arguments.get(parameter, '')))
            previous = m.end()
        processed.append(self.raw_line[previous:])
        return ''.join(processed)


@dataclasses.dataclass
class Statement:
    """A singular set of actions and resources."""

    effect: str
    actions: typing.List[str]
    resources: typing.Optional[typing.List[str]] = None
    principals: typing.Optional[typing.List[str]] = None

    def evaluate(
            self,
            action: str,
            resource: typing.Optional[str] = None,
            principal: typing.Optional[str] = None,
            arguments: typing.Dict[str, str] = None,
    ) -> typing.Optional[str]:
        """
        Evaluate the statement to determine if it allows, denys, or has no
        effect on the specified resource and action.

        :param action:
            The action being taken on the specified resource.
        :param resource:
            The resource on which the action is being taken.
        :param principal:
            The principal who desires to take the action.
        :param arguments:
            Arguments to pass into the policy before determining if
            access is allowed.
        :return:
            Either "allow", "deny" or None.
        """
        arguments = arguments if arguments else {}
        checks = [
            (action, self.actions),
            (resource, self.resources),
            (principal, self.principals),
        ]
        results = []
        for incoming, lines in checks:
            if incoming is None and lines is None:
                results.append(True)
                continue
            if incoming is None or lines is None:
                results.append(False)
                continue
            results.append(
                any(Line(l, arguments).is_match(incoming) for l in lines)
            )
        return self.effect if all(results) else None


@dataclasses.dataclass
class Policy:
    """An policy defining resource access."""

    statements: typing.List[Statement]
    builtin_args: typing.Dict[str, str] = None

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
        args = dict(arguments or {})
        args.update(self.builtin_args or {})
        evaluations = [
            statement.evaluate(action, resource, principal, args)
            for statement in self.statements
        ]
        if any(v == 'deny' for v in evaluations):
            return 'deny'
        if any(v == 'allow' for v in evaluations):
            return 'allow'
        return None

    @classmethod
    def load(
            cls, path: pathlib.Path, arguments: typing.Dict[str, str] = None
    ) -> "Policy":
        """Load the specified policy from yaml."""
        try:
            raw_yaml =  yaml.safe_load(path.read_text())
        except yaml.YAMLError:
            raise _errors.PolicyYamlInvalidError('Invalid policy yaml.')
        _validate_yaml(raw_yaml)
        statements = [
            Statement(
                statement['effect'],
                _force_to_list(statement['actions']),
                resources=(
                    _force_to_list(statement['resources'])
                    if 'resources' in statement else
                    None
                ),
                principals=(
                    _force_to_list(statement['principals'])
                    if 'principals' in statement else
                    None
                ),
            )
            for statement in raw_yaml['statements']
        ]
        return Policy(statements, arguments)

