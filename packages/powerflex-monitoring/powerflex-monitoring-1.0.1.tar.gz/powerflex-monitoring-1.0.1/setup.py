from os.path import dirname, join
from typing import Optional

from setuptools import find_packages, setup


def read(name, substitute: Optional[str] = None, **kwargs):
    try:
        with open(
            join(dirname(__file__), name), encoding=kwargs.get("encoding", "utf8")
        ) as openfile:
            return openfile.read()
    except OSError:
        if substitute is not None:
            return substitute
        raise


setup(
    name="powerflex-monitoring",
    packages=find_packages("src"),
    package_dir={"": "src"},
    zip_safe=True,
    version=read("src/powerflex_monitoring/VERSION", "UNKNOWN").strip(),
    package_data={"powerflex_monitoring": ["VERSION"]},
    include_package_data=True,
    description=" Tools to assist in monitoring a Python service.",
    long_description=read("README.md", "Unable to read README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/edf-re/powerflex_python_monitoring",
    project_urls={
        "Issue Tracker": "https://github.com/edf-re/powerflex_python_monitoring/issues",
    },
    install_requires=[
        "backoff>=2",
        "colorlog>=6",
        "nats-py>=2",
        "prometheus_client>=0.14",
        "pydantic>=1.9",
        "requests>=2",
        "starlette>=0.20",
        "types-requests>=2",
        "uvicorn>=0.18",
    ],
    python_requires=">2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*",
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
