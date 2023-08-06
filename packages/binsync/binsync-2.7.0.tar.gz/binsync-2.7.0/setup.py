
try:
    from setuptools import setup
    from setuptools import find_packages
    packages = find_packages()
except ImportError:
    from distutils.core import setup
    import os
    packages = [x.strip('./').replace('/','.') for x in os.popen('find -name "__init__.py" | xargs -n1 dirname').read().strip().split('\n')]

setup(
    name='binsync',
    version='2.7.0',
    packages=packages,
    install_requires=[
        "sortedcontainers",
        "toml",
        "GitPython",
        "filelock",
        "pycparser"
    ],
    description='Collaboration framework for binary analysis tasks.',
    long_description='Collaboration framework for binary analysis tasks.',
    long_description_content_type='text/markdown',
    url='https://github.com/angr/binsync',
)
