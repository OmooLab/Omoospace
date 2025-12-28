[中文文档](https://wcn96x0h20lt.feishu.cn/wiki/TAduwcqV3izhJ2kM3VpcZBW0n1d)

# Omoospace
![overview](docs/assets/overview.png)
Omoospace is a directory structure guideline for digital creation works. Its aim is universality, flexibility, and semantics not only for large projects and teamwork but also for small projects and solo work. Whether it is a 3d modeling task or a series production, it all fits.

If you are not sure how to design your project directory right, you can follow the omoospace rules, [click here to start](https://omoolab.github.io/Omoospace/latest/why-omoospace)


## Usage

1. Install uv
for windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

for macOS or linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

More info from https://docs.astral.sh/uv/getting-started/installation/

3. Install tool
```bash
uv tool install omoospace
```

2. Create omoospace
```bash
omoospace create
```

We provide some DCC plugins for CG artists to easily manage your projects following omoospace rules.

-   [Blender](https://omoolab.github.io/Omoospace/latest/plugins/blender)
-   [Houdini](https://omoolab.github.io/Omoospace/latest/plugins/houdini)

We also provide a python library for developing plugins, [read me for more info.](https://omoolab.github.io/Omoospace/latest/develop-plugin)
