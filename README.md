<h1 align="center">collegamento v0.1.1</h1>

A tool that makes it much easier to make offload work when asyncio isn't an option.

# Installation

In the Command Line, paste the following: `pip install collegamento`

## Description

Collegamento is a library that can be used for Client/Server IPC's with the goal of offloading major workloads to a second process. Docs are listed on this [ReadTheDocs page](https://collegamento.readthedocs.io/en/master/)

## Contributing

To contribute, fork the repository, make your changes, and then make a pull request. If you want to add a feature, please open an issue first so it can be discussed. Note that whenever and wherever possible you should try to use stdlib modules rather than external ones.

## Required Python Version: 3.11+

Albero will use the three most recent versions (full releases) going forward and will drop any older versions as new ones come out. This is because I hope to keep this package up to date with modern python versions as they come out instead of being forced to maintain decade old python versions.
Currently 3.11 is the minimum (instead of 3.10) as this was developed under 3.12 and there are many features that it relies on from this version I want. However, after 3.14 is released, the minimum version will be 3.12 (as would be expected from the plan) and will change accordingly in the future as is described in the plan above.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE).
