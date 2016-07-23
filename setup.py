from setuptools import setup

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2",
    "Topic :: Software Development :: Libraries",
]

setup(
    name='tappmq',
    version='0.0.1',
    py_modules=['tappmq'],
    url='https://github.com/gitguild/tappmq',
    license='MIT',
    classifiers=classifiers,
    author='Ira Miller',
    author_email='ira@gitguild.com',
    description='A message queue for the TAPP framework, using Redis and ' +\
                'sqlalchemy. ',
    setup_requires=['pytest-runner'],
    install_requires=[
        'redis',
        'bitjws'
    ],
    tests_require=['pytest', 'pytest-cov']
)
