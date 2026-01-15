import pytest
from pathlib import Path
from omoospace import make_path


def factory_make_item(main_dir: str = "."):
    @pytest.fixture()
    def make_item(mini_omoos_path: Path, request):
        file = request.param
        file = make_path(file, under=Path(mini_omoos_path, main_dir))

        yield file

        # delete all files
        # for file_path in file_paths:
        #     file_path.unlink(missing_ok=True)

    return make_item
