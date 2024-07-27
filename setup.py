# pip install -U -r requirements-dev.txt --break-system-packages; pip uninstall albero -y --break-system-packages; pip install . --break-system-packages --no-build-isolation; python3 -m pytest .
from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()


setup(
    name="PROJECT_NAME",
    version="0.1.0",
    description="PROJECT_NAME does xyz",
    author="Moosems",
    author_email="moosems.j@gmail.com",
    url="https://github.com/salve-org/PROJECT_NAME",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=open("requirements.txt", "r+")
    .read()
    .splitlines(keepends=False),
    python_requires=">=3.11",
    license="MIT license",
    classifiers=[
        # "Development Status :: 3 - Beta",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Typing :: Typed",
    ],
    packages=["PROJECT_NAME"],  # , "PROJECT_NAME.subpackages"],
)
