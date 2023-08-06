from setuptools import setup

setup(
    name="unrepl",
    packages=["unrepl"],
    version="1.0.2",
    include_package_data=True,
    long_description="unrepl",
    description="translated REPL code fragments to proper Python code",
    author="Ruud van der Ham",
    author_email="info@salabim.org",
    url="https://github.com/salabim/unrepl",
    download_url="https://github.com/salabim/unrepl",
    keywords=["repl"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
)
