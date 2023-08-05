from setuptools import setup
import os
import sys

_here = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(_here, 'podcast_app_user_agents', 'version.py')) as f:
    exec(f.read(), version)

setup(
    name='podcast_app_user_agents',
    version=version['__version__'],
    description=('Show how to structure a Python project.'),
    author='SoundOn',
    author_email='dev@soundon.fm',
    url='https://github.com/SoundOn/podcast-app-user-agents.py',
    license='MIT',
    packages=['podcast_app_user_agents'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6'],
    )