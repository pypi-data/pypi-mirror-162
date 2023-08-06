#! /usr/bin/env python

import setuptools

history = """
History
-------

0.0.1
+++++
released 2021-12-14

- Initial build

"""

description = 'Python DSL for setting up Flask app CDC'

setuptools.setup(
    name='avro-helper-devlibx',
    version="0.0.2",
    description='{0}\n\n{1}'.format(description, history),
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    author='devlibx',
    author_email='devlibxgithub@gmail.com',
    url='https://github.com/devlibx/avro-helper-py',
    packages=['avro_helper'],
    package_dir={"": "."},
    license='MIT',
    install_requires=[ "avro"]
)
