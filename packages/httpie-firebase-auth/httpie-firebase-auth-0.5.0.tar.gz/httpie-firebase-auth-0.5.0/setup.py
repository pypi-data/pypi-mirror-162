# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['httpie_firebase_auth']
install_requires = \
['google-auth>=2.9.1,<3.0.0', 'httpie>=3.2.1,<4.0.0', 'requests>=2.28.1,<3.0.0']

entry_points = \
{'httpie.plugins.auth.v1': ['httpie_firebase_auth = '
                            'httpie_firebase_auth:FirebaseAuthPlugin']}

setup_kwargs = {
    'name': 'httpie-firebase-auth',
    'version': '0.5.0',
    'description': 'An auth plugin for HTTPie that authenticates a user against Firebase',
    'long_description': '# HTTPie Firebase Auth Plugin\n\nThis project provides an authentication plugin for [HTTPie](https://httpie.io) that allows you to authenticate requests\nusing bearer tokens from [Firebase Auth](https://firebase.google.com/products/auth).\n\n## Instalation\n\nThe plugin can be installed with PIP.\n\n```bash\npip3 install --user httpie-firebase-auth\n```\n\nOnce installed, you should see the option ``firebase`` under `--auth-type` in `http --help` output. The `--auth`\nargument then accepts a username, password, and an optional project ID (`username:password[:project-id]`). If the\nproject ID is passed in the `auth` argument, it takes priority over the configuration file (outlined below).\n\n```bash\n# with username and password\nhttps --auth-type=firebase -a user@gmail.com:p@ssw0rd api.example.com\n\n# with username and password and project ID\nhttps --auth-type=firebase -a user@gmail.com:p@ssw0rd:my-project-id api.example.com\n```\n\n## Configuration\n\nThere are several steps to perform before the plugin can add authentication details to HTTP requests.\n\n### Projects\n\nAll project configuration happens in `${HTTPIE_CONFIG}/firebase/projects.json`. There is a section for `keys` that map a\nproject ID with an API key from the Firebase console. This key is the public web API key for the project.\n\n**NOTE:** The project IDs do not need to match the project ID on Firebase.\n\n### Endpoint mapping\n\nThe plugin allows HTTPie to determine the correct Firebase project to use to authenticate a given request. This means\nthat you can use different Firebase Auth projects for different endpoints. The endpoint section maps a project ID to a\nlist of hostname globs. There are two wildcard characters (`*` and `?`) for matching multiple characters or a single\ncharacter respectively. A default project can be specified as a fallback if none of the endpoints match.\n\n### Example configuration file\n\n```json\n{\n  "default": "project-1",\n  "keys": {\n    "project-1": "AIz....",\n    "project-2": "AIz...."\n  },\n  "endpoints": [\n    {\n      "project": "project-1",\n      "hosts": [\n        "localhost",\n        "api.example.com",\n        "*.example.io"\n      ]\n    },\n    {\n      "project": "project-2",\n      "hosts": [\n        "prod.example.com"\n      ]\n    }\n  ]\n}\n```\n\n## Credential Caching\n\nWhen a user is successfully authenticated against a Firebase project, the ID token and refresh token are cached in a\nproject specific file. On subsequent requests, if the provided email address is found in the project cache, the previous\nID token is used if it has not expired. If the token has expired, the refresh token is used to retrieve a new ID token.\nThe updated tokens are then stored in teh cache.\n\nWhen combined with [HTTPie sessions](https://httpie.io/docs/cli/sessions), the plugin is able to\ncontinue to authenticate requests for the user until the refresh token is no longer valid or revoked.\n\n## TODO\n\n- [ ] Document the `config.json`\n    - [x] How to add a project to api-key mapping\n    - [x] Structure for configuring which api-key/project is used for a set of hosts\n    - [ ] Add more details to the config spec\n    - [ ] Document credentials cache more completely\n',
    'author': 'Shane Farmer',
    'author_email': 'shane@secondbest.info',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/safarmer/httpie-firebase-auth',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
