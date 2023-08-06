# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['secscanner2junit']

package_data = \
{'': ['*']}

install_requires = \
['junit-xml>=1.9,<2.0']

entry_points = \
{'console_scripts': ['ss2ju = secscanner2junit:main']}

setup_kwargs = {
    'name': 'secscanner2junit',
    'version': '0.1.6',
    'description': 'Convert Security Scanner Output to JUnit Format',
    'long_description': "# SecScanner2JUnit\n[![PyPI version](https://badge.fury.io/py/secscanner2junit.svg)](https://badge.fury.io/py/secscanner2junit)\n\n[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/angrymeir/SecScanner2JUnit)\n\nGitLab offers [security scanning and visualization](https://docs.gitlab.com/ee/user/application_security/) directly via and on their platform.  \nOne nice feature is direct insights on merge requests. However, this feature is only available with the Ultimate tier. To also use this feature on the free tier, one can build around it by taking the security tool output, converting it to the JUnit format, and uploading it as JUnit report.\n\nTo summarize, this tool is for you if:\n- You use GitLab's free tier\n- You use Gitlabs [security templates](https://docs.gitlab.com/ee/user/application_security/)\n- You want to easily access security tool output in merge requests\n\nIf you are on the GitLabs Ultimate tier, just use their tooling! No need to mess up your `.gitlab-ci.yml` file. :smile:\n\n## Which scanning types are supported?\nAll scanning types available under the free tier:\n- Secret Scanning\n- Static Application Security Testing\n- Infrastructure as Code Scanning\n\n## How to use?\nProcedure:\n1. Overwrite the existing job so that the report can be used by future jobs.  \n2. Convert report\n3. Upload converted report as junit report\n\n**Example for Secret Scanning**  \nThis example can be used as is.\n```yaml\nstages:\n  - test\n  - convert\n  \n- include:\n  - template: Security/Secret-Detection.gitlab-ci.yml\n  \nsecret_detection:\n  artifacts:\n    paths:\n      - gl-secret-detection-report.json\n    when: always\n    \nsecret_convert:\n  stage: convert\n  dependencies:\n    - secret_detection\n  script:\n    - pip3 install SecScanner2JUnit\n    - ss2ju secrets gl-secret-detection-report.json gl-secret-detection-report.xml\n  artifacts:\n    reports:\n      junit: gl-secret-detection-report.xml\n```\n\n**Example for SAST**  \nSince GitLab decides dynamically which scanners to use depending on project languages, it makes sense to first perform a testrun only including the template. This way one can see which jobs are executed and then overwrite them. \n```yaml\nstages:\n  - test\n  - convert\n  \n- include:\n  - template: Security/SAST.gitlab-ci.yml\n  \nsemgrep-sast:\n  after_script:\n    - cp gl-sast-report.json gl-sast-semgrep-report.json\n  artifacts:\n    paths:\n      - gl-sast-semgrep-report.json\n    when: always\n\nbrakeman-sast:\n  after_script:\n    - cp gl-sast-report.json gl-sast-brakeman-report.json\n  artifacts:\n    paths:\n      - gl-sast-brakeman-report.json\n    when: always\n\nsemgrep-sast-convert:\n  stage: convert\n  dependencies:\n    - semgrep-sast\n  script:\n    - pip3 install SecScanner2JUnit\n    - ss2ju sast gl-sast-semgrep-report.json gl-sast-semgrep-report.xml\n  artifacts:\n    reports:\n      junit: gl-sast-semgrep-report.xml\n      \nbrakeman-sast-convert:\n  stage: convert\n  dependencies:\n     - brakeman-sast\n  script:\n    - pip3 install SecScanner2JUnit\n    - ss2ju sast gl-sast-brakeman-report.json gl-sast-brakeman-report.xml\n  artifacts:\n    reports:\n      junit: gl-sast-brakeman-report.xml\n\n```\n\n## Future Plans\n- [ ] Implement IaC Scanning\n",
    'author': 'Florian Angermeir',
    'author_email': 'florian.angermeir@tum.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/angrymeir/SecScanner2JUnit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
