from setuptools import setup, find_packages

import covid_nextstrain_collector

setup(
    name='covid_nextstrain_collector',
    version=covid_nextstrain_collector.__version__,
    description='Collector for sequencing information and accompanying metadata for SARS-CoV-2 samples at APL for visualization in Nextstrain',
    author='Andrew Lindsay',
    author_email='andrew.lindsay@aplabs.ca',
    url='https://github.com/provlab-bioinfo/covid-nextstrain-collector',
    packages=find_packages(exclude=('tests', 'tests.*')),
    python_requires='>=3.10,<3.11',
    install_requires=[
        "alive_progress==3.1.1",
        "numpy==1.24.2",
        "pandas==2.0.0",
        "pyahocorasick==2.0.0",
        "pytest==7.3.0",
        "requests==2.28.2",
    ],
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=[
        
    ],
    entry_points = {
        'console_scripts': [
            "covid-nextstrain-collector = covid_nextstrain_collector.__main__:main"
        ],
    }
)

