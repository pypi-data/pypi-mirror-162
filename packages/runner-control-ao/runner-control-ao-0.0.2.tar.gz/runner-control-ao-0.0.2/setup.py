from setuptools import setup, find_packages

setup(
    name="runner-control-ao",
    version="0.0.2",
    author="wangziling100",
    author_email="wangziling100@163.com",
    description="Exposed interface tool for runner service",
    package_dir={"": "src"},
    packages=find_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)