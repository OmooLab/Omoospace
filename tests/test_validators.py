from omoospace import is_number, is_email, is_url, is_version, is_autosave


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
    assert is_version("123") == False
    assert is_version("1.2.3") == True
    assert is_version("v1.2.3") == True
    assert is_version("v001") == True


def test_is_version():
    assert is_version("123") == False
    assert is_version("1.2.3") == True
    assert is_version("v1.2.3") == True
    assert is_version("v001") == True


def test_is_autosave():
    assert is_autosave("autosave") == True
    assert is_autosave("Auto-save") == True
    assert is_autosave("Auto_Save") == True
    assert is_autosave("auto save") == True
    assert is_autosave("abc Auto_Save") == False
    assert is_autosave("abc") == False
