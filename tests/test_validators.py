from omoospace import (
    is_number,
    is_email,
    is_url,
    is_version,
    is_autosave,
    is_buckup,
    is_recovered,
    is_ignore,
)


def test_is_number():
    assert is_number("abc") == False
    assert is_number("012") == True
    assert is_number("123") == True
    assert is_number("1.2") == True


def test_is_email():
    assert is_email("abc") == False
    assert is_email("abc@x") == False
    assert is_email("abc@x.com") == True


def test_is_url():
    assert is_url("abc") == False
    assert is_url("www.abc.com") == False
    assert is_url("https://www.example.com") == True


def test_is_version():
    valid_versions = [
        "v0.1.0",
        "0.1.0",
        "4.2",
        "v5.0",
        "20.0",
        "v001",
        "v002",
        "v260115",
        "v4",
        "v8",
        "0.1.0-alpha",
        "0.1.0-rc",
        "0.1.0-beta",
        "0.1.0-stable",
        "0.1.0-latest",
        "beta",
        "stable",
        "latest",
        "pre-alpha",
        ">=3.11",
        "^3.11",
        "~3.11",
        ">=0.2.0,<=1.0.0",
    ]

    # 非法的版本号
    invalid_versions = ["123", "001", "0001", "1001", "1.2..3", "abc"]

    # 测试合法版本号
    for version in valid_versions:
        assert is_version(version) is True

    # 测试非法版本号
    for version in invalid_versions:
        assert is_version(version) is False


def test_is_autosave():
    assert is_autosave("autosave") == True
    assert is_autosave("Auto-save") == True
    assert is_autosave("Auto_Save") == True
    assert is_autosave("auto save") == True
    assert is_autosave("abc Auto_Save") == False
    assert is_autosave("abc") == False


def test_is_buckup():
    assert is_buckup("Backup") == True
    assert is_buckup("backup") == True
    assert is_buckup("bak") == True
    assert is_buckup("bak1") == True
    assert is_buckup("bak001") == True
    assert is_buckup("back") == False
    assert is_buckup("backface") == False


def test_is_recovered():
    assert is_recovered("recovered") == True
    assert is_recovered("Recovered") == True
    assert is_recovered("Recovered001") == False
    assert is_recovered("recove") == False


def test_is_ignore_basic_patterns():
    """测试基本模式匹配"""
    # "content" 应该匹配所有层级的同名文件和文件夹
    assert is_ignore("content", ["content"]) == True
    assert is_ignore("sub/content", ["content"]) == False
    assert is_ignore("content/file.txt", ["content"]) == True
    assert is_ignore("sub/content/file.txt", ["content"]) == False
    assert is_ignore("different", ["content"]) == False


def test_is_ignore_directory_only():
    """测试目录专用模式（以/结尾）"""
    # "content/" 应该只匹配同名文件夹
    assert is_ignore("content/", ["content/"]) == True
    assert is_ignore("sub/content/", ["content/"]) == False
    assert is_ignore("content/file.txt", ["content/"]) == True
    assert is_ignore("sub/content/file.txt", ["content/"]) == False
    assert is_ignore("content", ["content/"]) == True  # 应该也匹配文件夹本身
    assert is_ignore("different", ["content/"]) == False
    assert is_ignore("different.txt", ["content/"]) == False


def test_is_ignore_wildcard():
    """测试通配符模式"""
    # "content/*" 应该匹配content文件夹下的直接子项
    assert is_ignore("content/file.txt", ["content/*"]) == True
    assert is_ignore("content/subdir", ["content/*"]) == True
    assert is_ignore("content/subdir/file.txt", ["content/*"]) == True
    assert is_ignore("content", ["content/*"]) == False


def test_is_ignore_multiple_patterns():
    """测试多个模式"""
    ignore_patterns = ["content", "*.log", "temp/"]
    assert is_ignore("content", ignore_patterns) == True
    assert is_ignore("file.log", ignore_patterns) == True
    assert is_ignore("sub/file.log", ignore_patterns) == True
    assert is_ignore("temp/file.txt", ignore_patterns) == True
    assert is_ignore("sub/temp/file.txt", ignore_patterns) == False
    assert is_ignore("normal.txt", ignore_patterns) == False


def test_is_ignore_string_input():
    """测试字符串输入（非列表）"""
    assert is_ignore("content", "content") == True
    assert is_ignore("sub/content", "content") == False
    assert is_ignore("different", "content") == False


def test_is_ignore_empty_ignore_list():
    """测试空的忽略列表"""
    assert is_ignore("content", []) == False
    assert is_ignore("sub/content", []) == False


def test_is_ignore_special_characters():
    """测试特殊字符处理"""
    assert is_ignore("file.txt", ["*.txt"]) == True
    assert is_ignore("file.py", ["*.txt"]) == False
    assert is_ignore("content123", ["content*"]) == True
    assert is_ignore("content.txt", ["content*"]) == True


def test_is_ignore_windows_paths():
    """测试Windows路径处理"""
    assert is_ignore("content\\file.txt", ["content/*"]) == True
    assert is_ignore("sub\\content", ["content"]) == False
    assert is_ignore("\\content\\file.txt", ["/content/*"]) == True
