#!/usr/bin/env python3
"""
Invoice OCR Parser Setup Script
Simple setup script for installing the package
"""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="ocrinvoice",
        version="1.0.0",
        description="Invoice OCR Parser - Extract structured data from PDF invoices using OCR",
        author="Invoice OCR Parser Team",
        author_email="support@ocrinvoice.com",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        python_requires=">=3.8",
        install_requires=[
            "pytesseract",
            "pdf2image",
            "pillow",
            "opencv-python",
            "pandas",
            "numpy",
            "click",
            "pyyaml",
            "pytest",
            "pytest-cov",
        ],
        extras_require={"dev": ["black", "flake8", "mypy", "pre-commit"]},
        entry_points={
            "console_scripts": [
                "ocrinvoice=ocrinvoice.cli.main:cli",
            ],
        },
        include_package_data=True,
        zip_safe=False,
    )
