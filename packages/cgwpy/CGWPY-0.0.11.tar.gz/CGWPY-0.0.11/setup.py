from setuptools import find_packages, setup


setup(
    name='CGWPY',
    packages=find_packages(include=['pgwpy']),
    version='0.0.11',
    description='Continuous Gravitational Waves library toolkit',
    author='Jules Perret',
    license='MIT',
    install_requires=['numba','numpy','astropy','gwpy','gwosc'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)
