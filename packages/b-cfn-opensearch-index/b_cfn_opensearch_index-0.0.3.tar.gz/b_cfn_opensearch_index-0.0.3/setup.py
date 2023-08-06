from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

with open('VERSION') as file:
    VERSION = file.read()
    VERSION = ''.join(VERSION.split())

setup(
    name='b_cfn_opensearch_index',
    version=VERSION,
    license='Apache License 2.0',
    packages=find_packages(exclude=[
        # Exclude virtual environment.
        'venv',
        '.venv',
        # Exclude test source files.
        'b_cfn_opensearch_index_tests'
    ]),
    description=(
        'AWS CDK based custom resource that manages an Opensearch index.'
    ),
    long_description=README + '\n\n' + HISTORY,
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=[
        'aws-cdk.core>=1.159.0,<2.0.0',
        'aws-cdk.aws_lambda>=1.159.0,<2.0.0',
        'aws-cdk.aws_opensearchservice>=1.159.0,<2.0.0',
        'b-aws-cf-response>=0.0.1,<1.0.0',
        'b-aws-testing-framework>=0.6.0,<1.0.0',
        'b-cfn-lambda-layer>=2.3.0,<3.0.0',
        'opensearch-py>=1.0.0,<2.0.0',
        'requests-aws4auth>=1.1.1,<2.0.0',
        'Faker>=10.0.0,<11.0.0'
    ],
    author='Gediminas Kazlauskas',
    author_email='gediminas.kazlauskas@biomapas.com',
    keywords='AWS CDK OpenSearch Index',
    url='https://github.com/Biomapas/B.CfnOpenSearchIndex.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
