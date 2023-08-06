# Whocan

Library for defining and determining access.

## Usage

### YAML usage

```yaml
statements:
- effect: allow
  actions:
  - workspace:Create*
  - workspace:Delete*
  - workspace:Get*
  - workspace:List*
  - workspace:Update*
  resources:
  - workspace:individual-${username}
```

```python
import pathlib
import whocan

policy = whocan.Policy.load(pathlib.Path('path-to-file.yaml'))
policy.is_allowed(
    resource='workspaces:individual-my-username',
    action='workspace:DeletePage',
    arguments={'username': 'my-username'},
)
# True
policy.is_allowed(
    resource='workspaces:individual-a-different-user',
    action='workspace:DeletePage',
    arguments={'username': 'my-username'},
)
# False
```

### Pure python usage

```python
import whocan

statement = whocan.Statement(
    resources=['workspaces:individual-${username}'],
    actions=[
        'workspace:Create*',
        'workspace:Delete*',
        'workspace:Get*',
        'workspace:List*',
        'workspace:Update*',
    ],
    effect='allow',
)

policy = whocan.Policy(statements=[statement])
policy.is_allowed(
    resource='workspaces:individual-my-username',
    action='workspace:DeletePage',
    arguments={'username': 'my-username'},
)
# True
policy.is_allowed(
    resource='workspaces:individual-a-different-user',
    action='workspace:DeletePage',
    arguments={'username': 'my-username'},
)
# False
```