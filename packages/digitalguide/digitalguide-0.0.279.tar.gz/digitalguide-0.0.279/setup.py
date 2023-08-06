from setuptools import find_packages, setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

test_deps = ['pytest',
             'flake8',
             "google-api-python-client",
             "google-auth-httplib2",
             "google-auth-oauthlib",
             "flask" ]

whatsapp_deps = ["twilio",
                 "quart",
                 "hypercorn",
                 ]

extras = {
    'test': test_deps,
    'whatsapp': whatsapp_deps
}

setup(
    name='digitalguide',
    packages=find_packages(),
    version='0.0.279',
    description='A Python Library to write digital guides for telegram',
    author='Soeren Etler',
    license='MIT',
    install_requires=["python-telegram-bot",
                      "ctparse",
                      "boto3",
                      "pymongo[srv]>= 3.4, < 4.0",
                      "mongoengine",
                      "Pillow",
                      "PyYAML",
                      "requests",
                      "python-json-logger"],
    setup_requires=['pytest-runner'],
    tests_require=test_deps,
    extras_require=extras,
    test_suite='tests',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
