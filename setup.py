from setuptools import setup, find_packages

setup(
    name="ecommerce-classifier",
    version="1.0.0",
    description="E-commerce product data classification and cleaning pipeline",
    author="Your Name",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ecom-classify=main:main",
        ]
    },
)
