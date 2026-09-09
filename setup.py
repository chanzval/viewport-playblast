#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for Viewport Playblast."""

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='viewport-playblast',
    version='1.0.0',
    author='Chanz Valmonte',
    author_email='chanzvalmonte@gmail.com',
    description='Professional viewport playblast tool for Autodesk Maya',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/viewport_playblast',
    packages=find_packages(exclude=['tests', 'docs', 'examples']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',
    keywords='maya playblast ffmpeg viewport video',
    project_urls={
        'Source': 'https://github.com/yourusername/viewport_playblast',
        'Bug Reports': 'https://github.com/yourusername/viewport_playblast/issues',
    },
    include_package_data=True,
    zip_safe=False,
)