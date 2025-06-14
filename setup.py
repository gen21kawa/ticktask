from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ticktask",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python CLI tool for seamless TickTick task management integration with Claude Code and Obsidian",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ticktask",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Scheduling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
        "python-dateutil",
        "pyyaml>=6.0",
        "cryptography",
        "rich>=13.0.0",
        "SQLAlchemy>=2.0",
        "aiofiles",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ]
    },
    entry_points={
        "console_scripts": [
            "ticktask=ticktask.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
)