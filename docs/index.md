[中文文档](https://wcn96x0h20lt.feishu.cn/wiki/TAduwcqV3izhJ2kM3VpcZBW0n1d)

# Omoospace
![overview](assets/overview.png)

Omoospace is a directory structure guideline for digital creation works. Its aim is universality, flexibility, and semantics not only for large projects and teamwork but also for small projects and solo work. Whether it is a 3d modeling task or a series production, it all fits.

If you are not sure how to design your project directory right, you can follow the [omoospace principles](principles)


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

1. Install tool
```bash
uv tool install omoospace
```

1. Create omoospace
```bash
omoospace init
```
