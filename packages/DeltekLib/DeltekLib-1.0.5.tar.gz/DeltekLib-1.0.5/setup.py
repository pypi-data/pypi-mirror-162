from setuptools import find_packages, setup
from DeltekLib.version import VERSION

setup(
    name='DeltekLib',
    packages=find_packages(include=['DeltekLib']),
    version=VERSION,
    description='Deltek Library',
    author='Deltek Systems (Philippines), Ltd.',
    author_email="testautomation@deltek.com",
    url="https://deltek.com/testautomation",
    license='Copyright',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: Free for non-commercial use'
    ],
)
