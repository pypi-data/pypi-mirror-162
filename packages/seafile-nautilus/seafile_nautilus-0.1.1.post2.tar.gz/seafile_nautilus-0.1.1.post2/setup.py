import codecs
import os.path

from setuptools import setup


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.strip().startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name='seafile_nautilus',
    version=get_version('seafile_nautilus/__version__.py'),
    packages=['seafile_nautilus'],
    url='https://gitlab.com/vinraspa/seafile-nautilus',
    license='MIT',
    author='Vincent Raspal',
    author_email='vincent.raspal@uca.fr',
    description='Seafile script for gnome-files (nautilus)',
    long_description=read('Readme.md'),
    long_description_content_type='text/markdown',
    install_requires=['requests'],
    entry_points={
        "console_scripts": [
            "seafile-nautilus = seafile_nautilus.main:main",
        ]
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: POSIX :: Linux',
        'Environment :: X11 Applications :: Gnome',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8'
    ]
)
