import glartifacts.version
import setuptools

from os import path

def long_description():
    readme = path.join(path.dirname(__file__), 'README.md')
    with open(readme, 'rt') as f:
        return f.read()

setuptools.setup(
    name='glartifacts',
    version=glartifacts.version.__version__,
    description='Tools for managing GitLab CI build artifacts',
    long_description = long_description(),
    long_description_content_type = 'text/markdown',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
	'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',

    ],
    license='MIT',
    keywords='GitLab',
    author='Mike Haboustak',
    author_email='haboustak@gmail.com',
    url='https://gitlab.com/haboustak/gitlab-artifact-tools',
    packages=[
        'glartifacts',
        'glartifacts.gitaly',
        'glartifacts.gitaly.proto',
        ],
    entry_points={
        'console_scripts': [
            'glartifacts = glartifacts.__main__:main',
        ]
    },
    install_requires=[
        'psycopg2>=2.6',
        'protobuf>=3.6.1',
        'grpcio>=1.15.0',
        'pyyaml>=3.11',
    ],
)
