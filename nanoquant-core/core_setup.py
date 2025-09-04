from setuptools import setup, find_packages

with open("CORE_README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("core_requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nanoquant-core",
    version="1.0.0",
    author="Swayam Singal",
    author_email="swayam8624@gmail.com",
    description="Extreme LLM Compression Engine - Compress large language models by up to 99.5%",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/swayam8624/nanoquant-core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "nanoquant=nanoquant.cli.core_main:app",
        ],
    },
    include_package_data=True,
    package_data={
        "nanoquant": ["core_requirements.txt"],
    },
)