from setuptools import setup, find_packages

setup(
    name="thebrain",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=1.10.0,<2.0.0",
        "typer>=0.7.0",
        "rich>=12.0.0",
        "pytest>=7.0.0",
        "sqlalchemy>=1.4.40",
        "sqlmodel>=0.0.8",
        "redis>=4.3.4",
        "httpx>=0.23.0",
        "fastapi>=0.95.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
    author="Samuel Audette",
    description="The Brain AI Scraper - Intelligent web scraping system",
)
