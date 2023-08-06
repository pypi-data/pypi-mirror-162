from typing import List

from setuptools import find_packages, setup

with open('README.md', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()


def requirements_packages() -> List[str]:
    with open('requirements.txt', encoding='utf-8') as f:
        requirements_lines = list(e.strip() for e in f.read().splitlines())
    return list(filter(lambda s: not s.startswith(('#', 'git+')), requirements_lines))


setup(
    name='code-discovery',
    version='0.0.7',
    author='Snowmate',
    author_email='support@snowmate.io',
    description='Code Discovery Tools',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['*tests*']),
    install_requires=requirements_packages(),
    scripts=["code_discovery/code_discovery"],
    package_dir={'code_discovery': 'code_discovery'},
)
