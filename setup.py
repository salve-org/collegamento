# pip install -U -r requirements-dev.txt --break-system-packages; pip uninstall collegamento -y --break-system-packages; pip install . --break-system-packages --no-build-isolation; python3 -m pytest .
from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()


setup(
    name="collegamento",
    version="0.2.0",
    description="Collegamento provides an easy to use Client/Server IPC backend",
    author="Moosems",
    author_email="moosems.j@gmail.com",
    url="https://github.com/salve-org/collegamento",
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
    packages=["collegamento", "collegamento.sclient_server"],
)
