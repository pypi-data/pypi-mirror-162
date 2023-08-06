#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sentry-feishu-wx",
    version='0.0.1',
    author='chengpeng',
    author_email='chengandpeng@gmail.com',
    url='https://github.com/chengandpeng/sentry_feishu',
    description='A Sentry extension which send errors stats to Feishu',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='sentry feishu',
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'sentry>=9.0.0',
        'requests',
    ],
    entry_points={
        'sentry.plugins': [
            'sentry_feishu = sentry_feishu.plugin:FeiShuPlugin'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 2.7',
        "License :: OSI Approved :: MIT License",
    ]
)
