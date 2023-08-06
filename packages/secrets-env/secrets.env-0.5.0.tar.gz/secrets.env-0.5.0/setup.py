# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['secrets_env']

package_data = \
{'': ['*']}

install_requires = \
['hvac>=0.11.2,<0.12.0', 'keyring>=23.6.0,<24.0.0', 'requests>=2.28.1,<3.0.0']

extras_require = \
{'toml:python_version < "3.11"': ['tomli>=2.0.1,<3.0.0'],
 'yaml': ['PyYAML>=6.0,<7.0']}

entry_points = \
{'poetry.application.plugin': ['poetry-secrets-env-plugin = '
                               'secrets_env.poetry:SecretsEnvPlugin']}

setup_kwargs = {
    'name': 'secrets.env',
    'version': '0.5.0',
    'description': 'Put secrets from Vault to environment variables',
    'long_description': '# secrets.env 🔓\n\n![test result](https://github.com/tzing/secrets.env/actions/workflows/test.yml/badge.svg)\n\nPut secrets from [Vault](https://www.vaultproject.io/) KV engine to environment variables like a `.env` loader. Without not landing data on disk.\n\nSecurity is important, but don\'t want it to be a stumbling block. We love secret manager, but the practice of getting secrets for local development could be dangerous- some of us put the sensitive data into a shell script and source it, which brings the risk of credential leaking.\n\nThis tool is built to *plug in* secrets into development without landing data on disk. Furthermore, we can safely commit the config file into CVS, for easily reproducing the environment, and reduce the risk of uploading the secrets to the server.\n\n\n## Usage\n\n> **Note**\n>\n> Standard CLI usage is not implemented yet.\n> Currently this app could only be used as a poetry plugin. Plugin is a poetry **1.2.0** feature, which is still in beta testing.\n\nGet it from this repository:\n\n```bash\n# add as poetry global plugin\npoetry self add \'git+https://github.com/tzing/secrets.env.git@trunk\' -E toml\n\n# add to project venv\npoetry add --dev \'git+https://github.com/tzing/secrets.env.git@trunk\' -E toml\n```\n\nFolowing extras avaliable:\n\n* `yaml`: supporting YAML config\n* `toml`: supporting TOML config, includes using `pyproject.toml`\n\nIf none of them are selected, this app only supports the config in JSON format.\n\n### With poetry\n\nYou can use this package as a [poetry plugin](https://python-poetry.org/docs/master/plugins/), then this app will pull the secrets from vault on poetry command `run` and `shell`.\n\n```bash\n# 1. install plugin\npoetry self add \'git+https://github.com/tzing/secrets.env.git@trunk\' -E yaml\n\n# 2. setup config\n#    read configuration section below for details\nexport VAULT_ADDR=\'https://example.com\'\nexport VAULT_METHOD=\'token\'\nexport VAULT_TOKEN=\'example-token\'\n\necho \'secrets:\'                       > .secrets-env.yaml\necho \'  FOO=secrets/default#example\'  > .secrets-env.yaml\n\n# 3. run\npoetry run sh -c \'echo $FOO\'\n```\n\n\n## Configure\n\n### Configuration file\n\nThis app searches for the file that matches following names in the current working directory and parent folders, and load the config from it. When there are more than one exists, the first one would be selected according to the order here:\n\n1. `.secrets-env.toml`[^1]\n2. `.secrets-env.yaml`[^2]\n3. `.secrets-env.yml`[^2]\n4. `.secrets-env.json`\n5. `pyproject.toml`[^1]\n\n[^1]: TOML format is only supported when either [tomllib](https://docs.python.org/3.11/library/tomllib.html) or [tomli](https://pypi.org/project/tomli/) is installed.\n[^2]: YAML format is only supported when [PyYAML](https://pypi.org/project/PyYAML/) is installed.\n\nAn example config in YAML format:\n\n```yaml\n# `source` configured the connection info to vault.\n# This is an *optional* section- values under section are required, but you can\n# provide them using environment variable.\nsource:\n  # Address to vault\n  # Could be replaced using `VAULT_ADDR` environment variable\n  url: https://example.com/\n\n  # Authentication info\n  # Schema for authentication could be complex, read section below.\n  auth:\n    method: okta\n    username: user@example.com\n\n# `secrets` lists the environment variable name, and the path the get the secret value\nsecrets:\n  # The key (VAR1) is the environment variable name to install the secret\n  VAR1:\n    # Path to read secret from vault\n    path: kv/default\n\n    # Path to identify which value to extract, as we may have multiple values in\n    # single secret in KV engine.\n    # For nested structure, join the keys with dots.\n    key: example.to.value\n\n  # Syntax sugar: path#key\n  VAR2: "kv/default#example.to.value"\n```\n\n> For most supported file format, they shared the same schema to this example. The only different is [`pyproject.toml`](./example/pyproject.toml) format- each section must placed under `tool.secrets-env` section, for aligning the community practice.\n> Visit [example folder](./example/) to read the equivalent expression in each format.\n\n### Authentication\n\nVault enforce authentication during requests, so we must provide the identity in order to get the secrets.\n\n#### Method\n\nSecrts.env adapts several auth methods. You must specify the auth method by either config file or the environment variable `VAULT_METHOD`. Here\'s the format in config file:\n\n```yaml\n---\n# standard layout\n# arguments could be included in `auth:`\nsource:\n  auth:\n    method: okta\n    username: user@example.com\n\n---\n# alternative layout\n# arguments must be avaliable in other source\nsource:\n  auth: token\n```\n\n#### Arguments\n\nArguments could be provided by various source: config file, environment variable and system keyring service.\n\nWe\'re using [keyring] package, which reads and saves the values from OSX [Keychain], KDE [KWallet], etc. For reading/saving value into keyring, use its [command line utility] with the system name `secrets.env`:\n\n[keyring]: https://keyring.readthedocs.io/en/latest/\n[Keychain]: https://en.wikipedia.org/wiki/Keychain_%28software%29\n[KWallet]: https://en.wikipedia.org/wiki/KWallet\n[command line utility]: https://keyring.readthedocs.io/en/latest/#command-line-utility\n\n```bash\nkeyring get secrets.env token/:token\nkeyring set secrets.env okta/test@example.com\n```\n\n#### Supported methods\n\nHere\'s required argument(s), their accepted source, and corresponding keys:\n\n##### `token`\n\n| key   | config file | env var        | keyring        |\n|-------|:------------|:---------------|:---------------|\n| token | ⛔️          | `VAULT_TOKEN`  | `token/:token` |\n\n##### `okta`\n\n| key      | config file | env var          | keyring               |\n|----------|:------------|:-----------------|:----------------------|\n| username | `username`  | `VAULT_USERNAME` | `okta/:username`      |\n| password | ⛔️          | `VAULT_PASSWORD` | `okta/YOUR_USER_NAME` |\n',
    'author': 'tzing',
    'author_email': 'tzingshih@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tzing/secrets.env',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
