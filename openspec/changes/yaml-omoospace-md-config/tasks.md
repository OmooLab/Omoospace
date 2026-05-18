## 1. YAML Format Support

- [x] 1.1 Update `Omoospace.__init__` to detect `.yaml` extension alongside `.yml`
- [x] 1.2 Update `Profile._read_profile()` to handle `.yaml` files

## 2. Lowercase Default Directory Names

- [x] 2.1 Update `create_omoospace` in `functions.py`: change `contents_dir` default from `"Contents"` to `"contents"`
- [x] 2.2 Update `create_omoospace` in `functions.py`: change `subspaces_dir` default from `"Subspaces"` to `"subspaces"`
- [x] 2.3 Update `Omoospace.subspaces_dir` property: change default from `or "Subspaces"` to `or "subspaces"`
- [x] 2.4 Update `Omoospace.contents_dir` property: change default from `or "Contents"` to `or "contents"`

## 3. OMOOSPACE.md as Default Config File

- [x] 3.1 Update `create_omoospace` in `functions.py`: generate `OMOOSPACE.md` instead of `Omoospace.yml` by default
- [x] 3.2 Update `create_omoospace` in `functions.py`: remove language-based filename logic (`Omoospace.{language}.yml`)
- [x] 3.3 Update `Omoospace.__init__` to prefer `OMOOSPACE.md` over `.yml`/`.yaml`

## 4. Remove Multi-language Config Support

- [x] 4.1 Remove `key_dict` from `language.py`
- [x] 4.2 Simplify `Profile._key()` method to return key directly without translation
- [x] 4.3 Simplify `ProfileItem._key()` method similarly
- [x] 4.4 Update `Profile.get()` to use key directly instead of `self._key(key)`
- [x] 4.5 Update `Profile.set()` to use key directly
- [x] 4.6 Update `ProfileItem.get()` and `ProfileItem.set()` similarly
- [x] 4.7 Remove `ALLOWED_LANGS` from `language.py` if no longer needed
- [x] 4.8 Update imports in `omoospace.py` and `functions.py` to remove unused references

## 5. Enable OMOOSPACE.md Write Support

- [x] 5.1 Update `Profile._write_profile()` to write to `.md` files using `frontmatter.dumps()` instead of switching to YAML
- [x] 5.2 Ensure `_write_profile()` preserves existing frontmatter structure when updating
- [x] 5.3 Test roundtrip: read from `OMOOSPACE.md`, modify, write back, verify changes persist