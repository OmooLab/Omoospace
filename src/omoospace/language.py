from typing import Literal


Language = Literal["en", "zh"]
ALLOWED_LANGS = {"en", "zh"}

key_dict = {
    "subspaces_dir": {"en": "subspaces_dir", "zh": "Subspaces文件夹"},
    "contents_dir": {"en": "contents_dir", "zh": "Contents文件夹"},
    "ignore": {"en": "ignore", "zh": "忽略列表"},
    "brief": {"en": "brief", "zh": "简述"},
    "notes": {"en": "notes", "zh": "记录列表"},
    "maker": {"en": "maker", "zh": "主创"},
    "makers": {"en": "makers", "zh": "主创列表"},
    "tools": {"en": "tools", "zh": "工具列表"},
    "works": {"en": "works", "zh": "作品列表"},
    "version": {"en": "version", "zh": "版本"},
    "email": {"en": "email", "zh": "邮箱"},
    "website": {"en": "website", "zh": "网站"},
    "extensions": {"en": "extensions", "zh": "扩展列表"},
    "contents": {"en": "contents", "zh": "内容列表"},
    "contributions": {"en": "contributions", "zh": "贡献列表"},
}
