# How to add modifier suffixes?

## Modifier Suffixes

When you have the same thing but in different versions, states, or with different notes, you can add modifier suffixes (separated by a dot `.`) to tell them apart. For example: 

`Skeleton.high.v001.blend`  

- `.high` indicates it’s a high‑poly version  
- `.v001` indicates the version number  

Both `.high` and `.v001` are modifier suffixes.


## Common Modifier Suffixes

| Suffix                                              | Meaning                                      |
| --------------------------------------------------- | -------------------------------------------- |
| `.`                                                 | A marker that the file cannot be overwritten |
| `.001`, `.002`, `.003`                              | Numbering without specific meaning           |
| `.001-modeling`, `.002-texturing`, `.003-animation` | Numbering with semantic meaning              |
| `.bak`                                              | Backup                                       |
| `.v001`, `.v002`, `.v003`                           | Version (usually placed last)                |
| `.v1.1`, `.v1.1.2`                                  | Version with major/minor numbers             |
| `.v251208`                                          | Version with date (YYMMDD)                   |
| `.sh0100`, `.sh0200`                                | Shot number                                  |
| `.left`, `.right`                                   | Side (for assets like left/right eye)        |
| `.karma`, `.arnold`, `.octane`, `.redshift`         | Renderer                                     |
| `.low`, `.high`                                     | Poly count level                             |
| `.256px`, `.1024px`, `.2048px`                      | Resolution                                   |
| `.1k`, `.2k`, `.4k`, `.540p`, `.1080p`              | Resolution                                   |
| `.basecolor`, `.sheencolor`, ...                    | Texture map type                             |
| `.depth`, `.indirectdiffuse`, ...                   | AOV type                                     |
| `.60fps`, `.30fps`                                  | Frame rate                                   |
| `.beauty`, `.clay`, `.wireframe`, `.viewport`       | Render style                                 |
| `.0001`, `.0002`, `.0003`                           | Frame number                                 |
| `.1001`, `.1002`, `.1003`                           | UDIM tile number                             |
| `.light`, `.layout`                                 | USD layer type                               |


## Example Structure

```bash
├── Seq010_Skeleton
├── Seq010_Skeleton.v001
│   ├── Seq010_Skeleton.low.glb
│   ├── Seq010_Skeleton.high.glb
│   ╰── Textures
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
