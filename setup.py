from setuptools import setup

from snout.api import __version__

links = []
requires = [
    'appdirs',
    'strictyaml',
    'click',
    'pyshark',
    'tabulate',
    'timeago',
]


def read_long_description():
    return ''


if __name__ == '__main__':
    setup(
        name='snout-api',
        version=__version__,
        url='https://github.com/snout-tools/snout-api',
        license='MIT',
        author='Johannes K Becker',
        author_email='jkbecker@bu.edu',
        maintainer='Johannes K Becker',
        maintainer_email='jkbecker@bu.edu',
        description='Plugin API for the SDR-Based Network Observation Utility Toolkit (Snout).',
        long_description=read_long_description(),
        packages=['snout.api'],
        include_package_data=True,
        zip_safe=False,
        platforms='any',
        install_requires=requires,
        extras_require={'dev': ['pytest', 'pytest-pep8', 'pytest-cov']},
        dependency_links=links,
        entry_points={
            'snout_plugins': [
                'apitest_ = snout.api.factory:Factory',
                'apitest_fancy = snout.api.factory:Factory',
            ],
        },
    )
