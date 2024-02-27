# Omoospace

[In Chinese](https://www.figma.com/proto/JsTmI3JwGQ3Q3qEThAJv15/Omoospace?page-id=0%3A1&type=design&node-id=1-2&viewport=-726%2C827%2C0.2&t=gOuR9PgBJRNM62R0-1&scaling=contain&mode=design)

Omoospace is a scalable directory structure solution for digital creation works. We provide a Python library for managing omoospace, including creating omoospace, shipping packages, setting subspace, etc.

[What is "Omoospace", and how does it rule all your creation files?](omoospace.md)

This library is for developing DCC plugins like blender add-ons to integrate omoospace into software. Remember, omoospace is just a directory guide. It should be easy to maintain manually. We do not recommend any over-design that only works by using plugins. This library aims to build plugins to avoid repetitive work and have a global view of the entire workspace structure, which consists of nested subspaces, not to manage a project entirely on a program without touching the folders.

We developed some plugins already:

-   [Houdini](https://github.com/OmooLab/Omoospace-Houdini)
-   [Blender](https://github.com/OmooLab/Omoospace-Blender)

## Usage

### [For CG Artists](artists.md)

### [For Plugin Developers](developers.md)

### [For Code Contributors](contributors.md)
