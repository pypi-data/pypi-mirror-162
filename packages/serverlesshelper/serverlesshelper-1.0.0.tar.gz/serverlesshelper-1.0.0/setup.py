
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name='serverlesshelper',
    version='1.0.0',
    author='Rajiv Sah',
    author_email='rajiv.shah01234@gmail.com',
    description='Demo Package for GfG Article.',
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    entry_points={
            'console_scripts': [
                'deploy=serverlesshelper.deploy:deploy'
            ]
    },
    install_requires=requirements,
    zip_safe=False
)
