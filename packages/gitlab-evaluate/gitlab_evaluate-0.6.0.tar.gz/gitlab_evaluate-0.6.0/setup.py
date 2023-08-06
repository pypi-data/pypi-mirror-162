# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gitlab_evaluate',
 'gitlab_evaluate.ci_readiness',
 'gitlab_evaluate.lib',
 'gitlab_evaluate.migration_readiness',
 'gitlab_evaluate.models']

package_data = \
{'': ['*'], 'gitlab_evaluate': ['data/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'gitlab-ps-utils>=0.5.0,<0.6.0',
 'pydantic>=1.8.2,<2.0.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['evaluate-ci-readiness = gitlab_evaluate.evaluate_ci:main',
                     'evaluate-gitlab = gitlab_evaluate.main:main']}

setup_kwargs = {
    'name': 'gitlab-evaluate',
    'version': '0.6.0',
    'description': 'Scans GitLab instance and ranks projects against a set of criteria. Can be used to identiy projects that may have too much metadata/size to reliably export or import.',
    'long_description': "# Evaluate\n\nEvaluate is a script that can be run to gather information about all projects of a GitLab\n\n- Instance\n- Group (including sub-groups)\n\nThis information is useful to the GitLab Professional Services (PS) team to accurately scope migration services.\n\n## Use Case\n\nGitLab PS plans to share this script with a Customer to run against their GitLab instance or group. Then the customer can send back the output files to enable GitLab engagement managers to scope engagements accurately. There are 3 output files.\n\nThe one to send back is the `report.txt` which lists config and project/group data possibly needing some special attention based on these [limits](#project-thresholds)\n\n## Install Method\n\n- [pip Install](#pip-install)\n- [Docker Container](#docker-container)\n  - [Bash](#local-usage)\n\n## Usage\n\n### System level data gathering\n\nEvaluate is meant to be run by an **OWNER** (ideally system **ADMINISTRATOR**) of a GitLab instance to gather data about every project on the instance or group (including sub-groups).\n\n1. A GitLab **OWNER** (ideally system **ADMINISTRATOR**) should provision an access token with `api` scope:\n   - [Personal access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token) for instance\n   - [Group access token](https://docs.gitlab.com/ee/user/group/settings/group_access_tokens.html#create-a-group-access-token-using-ui) for group\n2. Install `gitlab-evaluate` from the [Install](#install) section above,\n3. Run :point_down:\n\n    For evaluating a GitLab instance\n\n    ```bash\n    evaluate-gitlab -t <access-token-with-api-scope> -s https://gitlab.example.com\n    ```\n\n    For evaluating a GitLab group (including sub-groups)\n\n    ```bash\n    evaluate-gitlab -t <access-token-with-api-scope> -s https://gitlab.example.com -g 42\n    ```\n\n4. This should create a file called `evaluate_output.csv`\n5. If you're coordinating a GitLab PS engagement, email this file to the GitLab account team.\n\n### To gather CI data from a single repo\n\n```bash\n# For evaluating a single git repo's CI readiness\nevaluate-ci-readiness -r|--repo <git-repo-url>\n```\n\n### Command help screen\n\n```text\nusage: evaluate-gitlab [-h] [-t TOKEN] [-s SOURCE] [-f FILENAME] [-o] [-i] [-p PROCESSES] [-g GROUP_ID]\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -t TOKEN, --token TOKEN\n                        Personal Access Token: REQ'd\n  -s SOURCE, --source SOURCE\n                        Source URL: REQ'd\n  -f FILENAME, --filename FILENAME\n                        CSV Output File Name. If not set, will default to 'evaluate_output.csv'\n  -o, --output          Output Per Project Stats to screen\n  -i, --insecure        Set to ignore SSL warnings.\n  -p PROCESSES, --processes PROCESSES\n                        Number of processes. Defaults to number of CPU cores\n  -g GROUP_ID, --group GROUP_ID\n                        Group ID. Evaluate all group projects (including sub-groups)\n```\n\n```text\nusage: evaluate-ci-readiness [-h] [-r REPO]\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -r REPO, --repo REPO  Git Repository To Clone (ex: https://username:password@repo.com\n```\n\n### pip Install\n\n```bash\npip install gitlab-evaluate\n```\n\n## Docker Container\n\n[Docker containers with evaluate installed](https://gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate/container_registry) are also available to use.\n\n### Local Usage\n\n```bash\n# Spin up container\ndocker run --name evaluate -it registry.gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate:latest /bin/bash\n\n# In docker shell\nevaluate-ci-readiness -r|--repo <git-repo-url>\nevaluate-gitlab -t <access-token-with-api-scope> -s https://gitlab.example.com\n```\n\n### Example GitLab CI job using evaluate ci readiness script\n\n```yaml\nevaluate node-js:\n  stage: test\n  script:\n    - evaluate-ci-readiness --repo=https://github.com/nodejs/node.git\n  artifacts:\n    paths:\n      - node.csv\n```\n\nTo **test**, consider standing up a local docker container of GitLab. Provision an access token with `api` scope and **OWNER** (ideally system **ADMINISTRATOR**) privileges. Create multiple projects with varying number of commits, pipelines, merge requests, issues. Consider importing an open source repo or using [GPT](https://gitlab.com/gitlab-org/quality/performance) to add projects to the system.\n\n## Design\n\nDesign for the script can be found [here](https://gitlab.com/gitlab-com/customer-success/professional-services-group/ps-leadership-team/ps-practice-management/-/issues/83)\n\n## Project Thresholds\n\n_Below are the thresholds we will use to determine whether a project can be considered for normal migration or needs to have special steps taken in order to migrate_\n\n### Project Data\n\n- Pipelines - 1,500 max\n- Issues - 1,500 total (not just open)\n- Merge Requests - 1,500 total (not just merged)\n- Container images - 20GB per project\n- Packages - Any packages present\n\n### Repo Data\n\n- commits - 20K\n- branches - 1K\n- tags - 1K\n- Disk Size - 10GB\n",
    'author': 'GitLab Professional Services',
    'author_email': 'proserv@gitlab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0',
}


setup(**setup_kwargs)
