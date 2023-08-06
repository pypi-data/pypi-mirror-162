class BaseError(Exception):
    """The base error of Whocan."""


class PolicyEvaluationError(BaseError):
    """Policy could not be evaluated."""


class PolicyYamlInvalidError(BaseError):
    """The yaml cannot be transalted to a policy."""