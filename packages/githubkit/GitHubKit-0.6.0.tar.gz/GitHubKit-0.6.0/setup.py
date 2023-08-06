# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['githubkit',
 'githubkit.auth',
 'githubkit.cache',
 'githubkit.graphql',
 'githubkit.rest',
 'githubkit.webhooks']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<1.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'typing-extensions>=4.3.0,<5.0.0']

extras_require = \
{'all': ['anyio>=3.6.1,<4.0.0',
         'PyJWT>=2.4.0,<3.0.0',
         'cryptography>=37.0.4,<38.0.0'],
 'auth': ['anyio>=3.6.1,<4.0.0',
          'PyJWT>=2.4.0,<3.0.0',
          'cryptography>=37.0.4,<38.0.0'],
 'auth-app': ['PyJWT>=2.4.0,<3.0.0', 'cryptography>=37.0.4,<38.0.0'],
 'auth-oauth-device': ['anyio>=3.6.1,<4.0.0'],
 'jwt': ['PyJWT>=2.4.0,<3.0.0', 'cryptography>=37.0.4,<38.0.0']}

setup_kwargs = {
    'name': 'githubkit',
    'version': '0.6.0',
    'description': 'GitHub SDK for Python',
    'long_description': '<!-- markdownlint-disable MD033 MD041 -->\n<div align="center">\n\n[![githubkit](https://socialify.git.ci/yanyongyu/githubkit/image?description=1&descriptionEditable=%E2%9C%A8%20GitHub%20SDK%20for%20Python%20%E2%9C%A8&font=Bitter&language=1&pattern=Circuit%20Board&theme=Light)](https://github.com/yanyongyu/githubkit)\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/yanyongyu/githubkit/master/LICENSE">\n    <img src="https://img.shields.io/github/license/yanyongyu/githubkit" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/githubkit">\n    <img src="https://img.shields.io/pypi/v/githubkit" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.8+-blue" alt="python">\n  <a href="https://results.pre-commit.ci/latest/github/yanyongyu/githubkit/master">\n    <img src="https://results.pre-commit.ci/badge/github/yanyongyu/githubkit/master.svg" alt="pre-commit" />\n  </a>\n</p>\n\n<div align="center">\n\n<!-- markdownlint-capture -->\n<!-- markdownlint-disable MD036 -->\n\n_✨ The modern, all-batteries-included GitHub SDK for Python ✨_\n\n_✨ Support both **sync** and **async** calls, **fully typed** ✨_\n\n_✨ Always up to date, like octokit ✨_\n\n<!-- markdownlint-restore -->\n\n</div>\n\n## Installation\n\n```bash\npip install githubkit\n# or, use poetry\npoetry add githubkit\n# or, use pdm\npdm add githubkit\n```\n\n## Usage\n\n### Authentication\n\nInitialize a github client with no authentication:\n\n```python\nfrom githubkit import GitHub\n\ngithub = GitHub()\n# or, use UnauthAuthStrategy\ngithub = GitHub(UnauthAuthStrategy())\n```\n\nor using PAT (Token):\n\n```python\nfrom githubkit import GitHub, TokenAuthStrategy\n\ngithub = GitHub("<your_token_here>")\n# or, use TokenAuthStrategy\ngithub = GitHub(TokenAuthStrategy("<your_token_here>"))\n```\n\nor using GitHub APP authentication:\n\n```python\nfrom githubkit import GitHub, AppAuthStrategy\n\ngithub = GitHub(\n    AppAuthStrategy(\n        "<app_id>", "<private_key>", "<optional_client_id>", "<optional_client_secret>"\n    )\n)\n```\n\nor using GitHub APP Installation authentication:\n\n```python\nfrom githubkit import GitHub, AppInstallationAuthStrategy\n\ngithub = GitHub(\n    AppInstallationAuthStrategy(\n        "<app_id>", "<private_key>", installation_id, "<optional_client_id>", "<optional_client_secret>",\n    )\n)\n```\n\nor using OAuth APP authentication:\n\n```python\nfrom githubkit import GitHub, OAuthAppAuthStrategy\n\ngithub = GitHub(OAuthAppAuthStrategy("<client_id_here>", "<client_secret_here>"))\n```\n\nor using GitHub APP / OAuth APP web flow authentication:\n\n```python\nfrom githubkit import GitHub, OAuthWebAuthStrategy\n\ngithub = GitHub(\n    OAuthWebAuthStrategy(\n        "<client_id_here>", "<client_secret_here>", "<web_flow_exchange_code_here>"\n    )\n)\n```\n\nor using GitHub Action authentication:\n\n```python\nfrom githubkit import GitHub, ActionAuthStrategy\n\ngithub = GitHub(ActionAuthStrategy())\n```\n\n### Calling Rest API\n\n> APIs are fully typed. Typing in the following examples is just for reference only.\n\nSimple sync call:\n\n```python\nfrom githubkit import Response\nfrom githubkit.rest import FullRepository\n\nresp: Response[FullRepository] = github.rest.repos.get(owner="owner", repo="repo")\nrepo: FullRepository = resp.parsed_data\n```\n\nSimple async call:\n\n```python\nfrom githubkit import Response\nfrom githubkit.rest import FullRepository\n\nresp: Response[FullRepository] = await github.rest.repos.async_get(owner="owner", repo="repo")\nrepo: FullRepository = resp.parsed_data\n```\n\nCall API with context (reusing client):\n\n```python\nfrom githubkit import Response\nfrom githubkit.rest import FullRepository\n\n# with GitHub("<your_token_here>") as github:\nwith github:\n    resp: Response[FullRepository] = github.rest.repos.get(owner="owner", repo="repo")\n    repo: FullRepository = resp.parsed_data\n```\n\n```python\nfrom githubkit import Response\nfrom githubkit.rest import FullRepository\n\n# async with GitHub("<your_token_here>") as github:\nasync with github:\n    resp: Response[FullRepository] = await github.rest.repos.async_get(owner="owner", repo="repo")\n    repo: FullRepository = resp.parsed_data\n```\n\n### Pagination\n\n```python\nfrom githubkit.rest import Issue\n\nfor issue in github.paginate(\n    github.rest.issues.list_for_repo, owner="owner", repo="repo", state="open"\n):\n    issue: Issue\n    print(issue.number)\n```\n\n```python\nfrom githubkit.rest import Issue\n\nasync for issue in github.paginate(\n    github.rest.issues.async_list_for_repo, owner="owner", repo="repo", state="open"\n):\n    issue: Issue\n    print(issue.number)\n```\n\n### Calling GraphQL API\n\nSimple sync call:\n\n```python\ndata: Dict[str, Any] = github.graphql(query, variables={"foo": "bar"})\n```\n\nSimple async call:\n\n```python\ndata: Dict[str, Any] = github.async_graphql(query, variables={"foo": "bar"})\n```\n\n### Webhook Verification\n\nSimple webhook payload verification:\n\n```python\nfrom githubkit.webhooks import verify\n\nvalid: bool = verify(secret, request.body, request.headers["X-Hub-Signature-256"])\n```\n\nSign the webhook payload manually:\n\n```python\nfrom githubkit.webhooks import sign\n\nsignature: str = sign(secret, payload, method="sha256")\n```\n\n### Webhook Parsing\n\nParse the payload with event name:\n\n```python\nfrom githubkit.webhooks import parse, WebhookEvent\n\nevent: WebhookEvent = parse(request.headers["X-GitHub-Event"], request.body)\n```\n\nParse the payload without event name (may cost longer time):\n\n```python\nfrom githubkit.webhooks import parse_without_name, WebhookEvent\n\nevent: WebhookEvent = parse_without_name(request.body)\n```\n\nParse dict like payload:\n\n```python\nfrom githubkit.webhooks import parse_obj, parse_obj_without_name, WebhookEvent\n\nevent: WebhookEvent = parse_obj(request.headers["X-GitHub-Event"], request.json())\nevent: WebhookEvent = parse_obj_without_name(request.json())\n```\n\n### Switch between AuthStrategy\n\nYou can change the auth strategy and get a new client simplely using `with_auth`.\n\nChange from `AppAuthStrategy` to `AppInstallationAuthStrategy`:\n\n```python\nfrom githubkit import GitHub, AppAuthStrategy\n\ngithub = GitHub(AppAuthStrategy("<app_id>", "<private_key>"))\ninstallation_github = github.with_auth(\n    github.auth.as_installation(installation_id)\n)\n```\n\nChange from `OAuthAppAuthStrategy` to `OAuthWebAuthStrategy`:\n\n```python\nfrom githubkit import GitHub, OAuthAppAuthStrategy\n\ngithub = GitHub(OAuthAppAuthStrategy("<client_id>", "<client_secret>"))\nuser_github = github.with_auth(github.auth.as_web_user("<code>"))\n```\n',
    'author': 'yanyongyu',
    'author_email': 'yyy@yyydl.top',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yanyongyu/githubkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
