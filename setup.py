from setuptools import setup, find_packages

setup(
    name="lc_python_core",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-adk>=0.1.0",
        "pydantic>=1.10,<2.0"
    ],
    python_requires='>=3.8',
)
