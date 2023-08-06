from setuptools import setup
import os


root_path = os.path.join(os.path.dirname(__file__))
file = open(os.path.join(root_path, "README.md"))
readme_file = file.read()
file.close()

install_package_requires = [
    "boto3>=1.24,<2",
]

setup(
    name="eb-aws-sso",
    version="0.0.7",
    python_requires=">=3.8",
    scripts=["awssso"],
    install_requires=install_package_requires,
    long_description=readme_file,
    url="https://github.com/ebanalyse/awssso",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)
