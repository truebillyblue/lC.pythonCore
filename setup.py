from setuptools import setup, find_packages

def get_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f.readlines() if not line.startswith("#")]

setup(
    name="lc_python_core",
    version="0.1.0", # Initial version
    author="Learnt.Cloud Initiative",
    author_email="[placeholder_email@example.com]", # Replace if a real one is available
    description="Core Python services and schemas for the Learnt.Cloud project, supporting ComfyUI custom nodes and other frontends.",
    long_description="This package contains Standard Operating Procedures (SOPs), data schemas (Pydantic models like MadaSeed), and backend services for MADA interaction, PBI management, and agent integrations (API, Web).",
    url="[placeholder_repository_url]", # Replace if a real one is available
    packages=find_packages(exclude=['tests', 'tests.*']), # Automatically find packages like 'schemas', 'services', 'sops'
    install_requires=get_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", # Assuming MIT, adjust if different
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.8', # Specify a reasonable minimum Python version
)
