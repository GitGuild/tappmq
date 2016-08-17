from setuptools import setup

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2",
    "Topic :: Software Development :: Libraries",
]

setup(
    name='tappmq',
    version='0.0.2',
    packages=['tappmq'],
    url='https://github.com/gitguild/tappmq',
    license='MIT',
    classifiers=classifiers,
    author='Ira Miller',
    author_email='ira@gitguild.com',
    description='A message queue for the TAPP framework, using Redis and ' +
                'sqlalchemy. ',
    setup_requires=['pytest-runner'],
    install_requires=[
        'redis',
        'sqlalchemy',
        'sqlalchemy_models',
        'tapp-config',
        'bitjws',
        'supervisor'
    ],
    tests_require=['pytest', 'pytest-cov'],
    entry_points="""
[console_scripts]
tapplistener = tappmq.eventlistener:main
"""
)
