# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snyk_tags']

package_data = \
{'': ['*']}

install_requires = \
['PyGithub>=1.55,<2.0',
 'colorama>=0.4.5,<0.5.0',
 'httpx>=0.23.0,<0.24.0',
 'pysnyk>=0.9.3,<0.10.0',
 'rich>=10.11.0',
 'shellingham>=1.4.0,<2.0.0',
 'typer>=0.5.0']

entry_points = \
{'console_scripts': ['snyk-tags = snyk_tags.tags:app']}

setup_kwargs = {
    'name': 'snyk-tags',
    'version': '0.9.0',
    'description': 'Tool designed to add tags in bulk to Snyk projects',
    'long_description': "# Snyk Tags Tool\n\nSnyk Tags is a CLI tool which can:\n\n- Help filter Snyk projects by product type by adding product tags across a Snyk Group or Organization - using ```snyk-tags tag```\n- Help filter Snyk projects by applying tags to a target import (for example a git repo like **snyk-labs/nodejs-goof**) - using ```snyk-tags target tag``` or from a csv/json file with ```snyk-tags fromfile target-tag```\n- Help filter Snyk projects by applying attributes to a target import (for example a git repo like **snyk-labs/nodejs-goof**) - using ```snyk-tags target attributes``` or from a csv/json file with ```snyk-tags fromfile target-attributes```\n- Help filter Snyk projects by adding the GitHub Code Owner as a tag to target import (must be a GitHub repo in the form **snyk-labs/nodejs-goof**) - using ```snyk-tags target github```\n- Help with tag management by removing tags from a Group or a target import (for example a git repo like **snyk-labs/nodejs-goof**) - using ```snyk-tags target remove``` or listing all tags using ```snyk-tags list tags``` (also in bulk or from a csv/json file with ```snyk-tags fromfile```)\n\n### snyk-tags tag\n\n```snyk-tags tag``` is a CLI tool that uses the Snyk Project Tag API to assign tags in bulk to Snyk projects based on the product.\n\n```snyk-tags tag``` will update all projects of the specified product within a Snyk Group or Organization with the product's tag.\n\nYou can also specify a custom tag for the specific project types.\n\n[List all project types](#list-of-all-project-types)\n\n### snyk-tags target\n\n```snyk-tags target``` goes through a target (repo, container, CLI import) to assign tags, attributes and assign the GitHub code owner. Targets in snyk can be varied like:\n\n- **snyk-labs/nodejs-goof** is the target from a git import\n- **library/httpd** is the target from a container import\n- **/snyk-labs/nodejs-goof** is the target from a CLI import\n\nYou can use:\n\n- **```snyk-tags target tag```** to add tags to a target\n- **```snyk-tags target attributes```** to add attributes to a target\n- **```snyk-tags target github```** to add the GitHub Code Owner as a tag to a target. The GitHub repo must include the GitHub Organization e.g. **snyk-labs/nodejs-goof**\n\n[List all possible attributes](#list-of-all-attributes)\n\n### Viewing results\n\nOnce you run ```snyk-tags```, go into the UI, naviagate to the projects page and find the tags filter or attribute filter options on the left-hand menu. Select the tag/attribute you have applied and you will see all projects associated.\n\n## Installation and requirements\n\n### Requirements\n\nRequires Python version above 3.6\n\n### Installation\n\nTo install the simplest way is to use pip:\n\n```bash\npip install snyk-tags\n```\n\nAlternatively you can clone the repo and then run the following commands:\n\n```python\npoetry install # To install dependencies\npython -m snyk-tags # To run snyk-tags\n```\n\n## Examples\n\nI want to filter all my Snyk Code projects to the whole Snyk Group:\n\n``` bash\nsnyk-tags tag sast --group-id=abc --snyktkn=abc\n```\n\nI want to filter all my ```npm``` Snyk Open Source projects within a specific Snyk Organization:\n\n``` bash\nsnyk-tags tag sca --scatype=npm --org-id=abc --snyktkn=abc\n```\n\nI want to filter all projects within my ```snyk-labs/nodejs-goof``` repo by ```project:snyk```\n\n``` bash\nsnyk-tags target tag --target=snyk-labs/nodejs-goof --org-id=abc --snyktkn=abc --tagkey=project --tagvalue=snyk\n```\n\nI want to add attributes to all projects within my ```snyk-labs/python-goof``` repo. The attributes are ```critical, production, backend```\n\n``` bash\nsnyk-tags target attributes  --target=snyk-labs/python-goof --org-id=abc --snytkn=abc --criticality=critical --environment=backend --lifecycle=production\n```\n\nI want mark with the repo owner all projects of the repo ```snyk-labs/nodejs-goof``` so I can filter by owner e.g.```Owner:EricFernandezSnyk```\n\n``` bash\nsnyk-tags target github --target=snyk-labs/nodejs-goof --org-id=abc --snyktkn=abc --githubtkn=abc\n```\n\nI want to remove the tag project:snyk from the repo ```snyk-labs/nodejs-goof```\n\n``` bash\nsnyk-tags remove tag-from-target --target=snyk-labs/nodejs-goof --group-id=abc --snyktkn=abc --tagkey=project --tagkey=snyk\n```\n\nI want to filter all projects within ```snyk-labs/nodejs-goof``` and ```snyk-labs/goof``` repo by ```project:snyk``` so I use a csv in the format ```org-id,target,key,value```\n\n``` bash\nsnyk-tags fromfile target-tag --file=path/to/file.csv --snyktkn\n```\n\n## Types of projects and attributes\n\n### List of all project types\n\n|       Snyk IaC       | Snyk Open Source | Snyk Container | Snyk Code |\n|:--------------------:|:----------------:|:--------------:|:---------:|\n|    terraformconfig   |       maven      |   dockerfile   |    sast   |\n|     terraformplan    |        npm       |       apk      |           |\n|       k8sconfig      |       nuget      |       deb      |           |\n|      helmconfig      |      gradle      |       rpm      |           |\n| cloudformationconfig |        pip       |      linux     |           |\n|       armconfig      |       yarn       |                |           |\n|                      |     gomodules    |                |           |\n|                      |     rubygems     |                |           |\n|                      |     composer     |                |           |\n|                      |        sbt       |                |           |\n|                      |     golangdep    |                |           |\n|                      |     cocoapods    |                |           |\n|                      |      poetry      |                |           |\n|                      |     govendor     |                |           |\n|                      |        cpp       |                |           |\n|                      |  yarn-workspace  |                |           |\n|                      |        hex       |                |           |\n|                      |       paket      |                |           |\n|                      |      golang      |                |           |\n\n### List of all attributes\n\n| Criticality          | Environment | Lifecycle       |\n|:--------------------:|:-----------:|:---------------:|\n|       critical       |   frontend  |    production   |\n|         high         |   backend   |   development   |\n|        medium        |   internal  |     sandbox     |\n|          low         |   external  |                 |\n|                      |    mobile   |                 |\n|                      |     saas    |                 |\n|                      |    onprem   |                 |\n|                      |    hosted   |                 |\n|                      | distributed |                 |\n",
    'author': 'EricFernandezSnyk',
    'author_email': 'eric.fernandez@snyk.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/EricFernandezSnyk/snyk-tags-tool',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
