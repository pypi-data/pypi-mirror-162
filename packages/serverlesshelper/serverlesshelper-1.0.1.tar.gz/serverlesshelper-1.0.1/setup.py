
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name='serverlesshelper',
    version='1.0.1',
    author='Rajiv Sah',
    author_email='rajiv.shah01234@gmail.com',
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    entry_points={
            'console_scripts': [
                'deploy=serverlesshelper.deploy:deploy',
                'logs=serverlesshelper.logs:logs',
            ]
    },
    install_requires=requirements,
    zip_safe=False
)
