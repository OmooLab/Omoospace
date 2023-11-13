# Omoospace

Omoospace is a scalable directory structure solution for digital creation works. We provide a Python library for managing omoospace, including creating omoospace, shipping packages, setting subspace, etc.

[What is "Omoospace", and how does it rule all your creation files?](omoospace.md)

This library is for developing DCC plugins like blender add-ons to integrate omoospace into software. But remember, omoospace is just a directory guide. It should be easy to maintain manually. We do not recommend any over-design that only works by using the plugin. This library aims to build plugins to avoid repetitive work and have a more global view of the whole project structure, which consists of nested subspaces, not to manage a project entirely on a program without touching the folders.

## Installation

This library requires Python version 3.9 or above (python official download link). You can use pyenv or conda for managing multiple Python versions on a single machine.

Run the following command to install omoospace:

```shell
pip install omoospace
```

## Usage

[For Developers](developers.md)