import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name='g2m-api-client',
    version='1.2.31',
    description='Analyzr API Client',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://analyzr.ai",
    author='Analyzr Team',
    author_email='support@analyzr.ai',
    license='Proprietary',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=['g2mclient'],
    install_requires=[
        "scikit-learn",
    ]
)
