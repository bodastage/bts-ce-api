from setuptools import setup

setup(
    name='btsapi',
    packages=['btsapi'],
    version="1.0.11",
    url="https://github.com/bodastage/bts-ce-api",
    author="Emmanuel Robert Ssebaggala",
    author_email="emmanuel.ssebaggala@bodastage.com",
    description="REST API for Boda Telecom Suite Community Edition (BTS-CE). An open source vendor agnostic telecommunication network management platform",
    include_package_data=True,
    install_requires=[
        'flask',
        'sqlalchemy',
        'marshmallow',
        'flask-sqlalchemy',
        'flask-jsontools',
        'flask-marshmallow',
        'marshmallow-sqlalchemy',
        'flask-bcrypt',
        'flask-testing',
        'flask-cors',
        'sqlalchemy-datatables',
        'flask-login',
        'blinker'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
        classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)