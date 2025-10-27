from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sudodog",
    version="0.1.0",
    author="SudoDog",
    author_email="support@sudodog.com",  # Or use your GitHub email
    description="Secure sandbox for AI agents. Blocks dangerous operations, monitors behavior, full audit trail.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SudoDog-official/sudodog",
    project_urls={
        "Bug Tracker": "https://github.com/SudoDog-official/sudodog/issues",
        "Documentation": "https://github.com/SudoDog-official/sudodog#readme",
        "Homepage": "https://sudodog.com",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
    ],
    keywords="ai-agents security sandbox monitoring audit-trail langchain",
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.0",
        "rich>=13.7.0",
        "psutil>=5.9.0",
        "pyyaml>=6.0",
        "watchdog>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "sudodog=sudodog.cli:cli",
        ],
    },
)
