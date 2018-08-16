import time
from setuptools import setup, find_packages

version = '0.9.0'

install_requires = [
    'PyYAML==3.12',
]

tests_require = [ 'pytest>=3.0.3', 'mock', 'pytest-mock', 'coverage' ]

setup_config = {
    'name': 'yaml-inc',
    'version': version,
    'packages': find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    'install_requires': install_requires,
    'tests_require': tests_require,
    'include_package_data': True
}

if __name__ == '__main__':
    setup(**setup_config)
