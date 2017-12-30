from setuptools import setup

setup(
    name='btsapi',
    packages=['btsapi'],
    include_package_data=True,
    install_requires=[
        'flask',
		'flask-sqlalchemy'
    ],
	setup_requires=[
        'pytest-runner',
    ],
	tests_require=[
        'pytest',
    ],
)