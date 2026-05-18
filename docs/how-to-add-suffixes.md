# 如何设置前缀、后缀？

## 语境前缀

如果两个事物有重名的可能，可以通过前缀添加语境来区分（用下划线`_`连接）。

例如项目中有两个动画，都有`Sc010.blend`，那么常见的做法是把他们放在两个文件夹中，但是你也可以在前面加上动画名作为语境，比如`Short01_Sc010.blend`、`Short02_Sc010.blend`。`Short01_`和`Short02_`都是**语境前缀**

语境前缀的本质就是“文件夹”。

## 修饰后缀

同一事物，但是不同版本、不同状态、不同备注，可以通过后缀添加修饰来区分（用英文点`.`连接）。

例如`骨骼模型.high.v001.blend`，`.high`点明了是高面数模型，`.v001`点明了版本号。`.high`和`.v001`都是**修饰后缀**
  

### 常见修饰后缀

| **修饰后缀**                                                     | 语义              |
| ------------------------------------------------------------ | --------------- |
| .                                                            | 文件无法覆盖的标识       |
| .001, .002, .003                                             | 无语义编号           |
| .001-modeling,<br><br>.002-texturing,<br><br>.003-animation  | 加序号并添加语义，用-作为连接 |
| .bak                                                         | 备份              |
| .v001, .v002, .v003<br><br>.v1.1, .v1.1.2<br><br>.v251208    | 版本（置于最后）        |
| .left, .right                                                | 方位              |
| .karma, .arnold, .octane, .redshift                          | 渲染器             |
| .low, .high                                                  | 面数              |
| .256px, .1024px, .2048px<br><br>.1k, .2k, .4k, .540p, .1080p | 视频/图片分辨率        |
| .basecolor, .sheencolor,...                                  | 贴图图层            |
| .depth, .indrectdiffuse...                                   | AOVs            |
| .60fps, .30fps                                               | 视频帧率            |
| .beauty<br><br>.clay<br><br>.wireframe<br><br>.viewport      | 渲染风格            |
| .0001, .0002, .0003                                          | 帧序号             |
| .1001, .1002, .1003                                          | UDIM            |


## 示例

```Bash
├── Seq010_Skeleton
├── Seq010_Skeleton.v001
│   ├── Seq010_Skeleton.low.glb
│   ├── Seq010_Skeleton.high.glb
│   ╰── textures
│       ├── Seq010_Skeleton.basecolor.1k.png
│       ├── Seq010_Skeleton.basecolor.2k.png
│       ├── Seq010_Skeleton.roughness.1k.png
│       ╰── Seq010_Skeleton.roughness.2k.png
├── Seq010_Shot0100
│   ├── Seq010_Shot0100.0001.png
│   ├── Seq010_Shot0100.0002.png
│   ├── ...
│   ╰── Seq010_Shot0100.0360.png
```