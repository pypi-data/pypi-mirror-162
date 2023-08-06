from setuptools import setup
import os

install_package_requires = [
    "boto3>=1.24,<2",
]

setup(
    name="eb-aws-sso",
    version="0.0.6",
    python_requires=">=3.8",
    scripts=["awssso"],
    install_requires=install_package_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)
