import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AVMWeather",
    version="1.0.0",
    author="AlejandroV",
    author_email="avmmodules@gmail.com",
    description="Get weather data in a simple way.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/avmmodules/AVMWeather",
    project_urls={
        "Bug Tracker": "https://github.com/avmmodules/AVMWeather/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6"
)