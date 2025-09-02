from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cookie-creator",
    version="1.0.0",
    author="Alex Scott & the BrowserVM Project",
    author_email="",
    description="Interactive cookie creator utility with yt-dlp integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/myschoolstory/cookie-creator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Multimedia :: Video",
        "License :: Apache 2.0 License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "ytdlp": ["yt-dlp>=2023.1.6"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "cookie-util=cookie_creator.cookie_creator:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)