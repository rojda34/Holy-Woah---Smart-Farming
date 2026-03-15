"""
KATS - Urban Rooftop Farming AI System
Setup configuration for package installation
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="kats-farm",
    version="1.0.0",
    author="KATS Development Team",
    author_email="team@kats-farm.com",
    description="AI-Powered Decision Support System for Urban Rooftop Farming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_ORG/KATS",
    project_urls={
        "Bug Tracker": "https://github.com/YOUR_ORG/KATS/issues",
        "Documentation": "https://github.com/YOUR_ORG/KATS/wiki",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Farmers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "kats=src.app:run",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
