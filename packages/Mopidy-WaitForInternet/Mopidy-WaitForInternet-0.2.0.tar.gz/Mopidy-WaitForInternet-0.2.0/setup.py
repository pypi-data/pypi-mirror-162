import re

from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-WaitForInternet',
    version=get_version('mopidy_waitforinternet/__init__.py'),
    url='https://github.com/DavisNT/mopidy-waitforinternet',
    license='Apache License, Version 2.0',
    author='Davis Mosenkovs',
    author_email='python-apps@dm.id.lv',
    description='Mopidy extension that waits for internet connection during early startup.',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    python_requires='>= 3.7',
    install_requires=[
        'setuptools',
        'requests',
        'Mopidy >= 3.0',
    ],
    entry_points={
        'mopidy.ext': [
            'waitforinternet = mopidy_waitforinternet:WaitForInternetExtension',
            'waitfortimesync = mopidy_waitfortimesync:WaitForTimeSyncExtension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
