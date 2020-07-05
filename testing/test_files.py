import os
from pathlib import Path

import pytest

from koneko import files


def test_find_mode2_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr('koneko.files.KONEKODIR', tmp_path)
    (tmp_path / '1234' / 'individual').mkdir(parents=True)
    (tmp_path / '5678' / '1').mkdir(parents=True)
    assert files.find_mode2_dirs() == ['1234']


def test_verify_full_download():
    assert files.verify_full_download("testing/files/008_77803142_p0.png") is True
    assert files.verify_full_download("testing/files/not_an_image.txt") is False
    # The above code will remove the file
    os.system("touch testing/files/not_an_image.txt")

def test_dir_not_empty(tmp_path):
    class FakeData:
        def __init__(self):
            self.download_path = tmp_path
            self.first_img = "004_祝！！！.jpg"
            self.all_names = ["004_祝！！！.jpg", '008_77803142_p0.png', '017_ミコニャン.jpg']

    data = FakeData()

    # Test dir exists but is empty
    tmp_path.mkdir(exist_ok=True)
    data.download_path = tmp_path
    assert files.dir_not_empty(data) is False

    # Copy .koneko and only one image to that dir
    (tmp_path / '.koneko').touch()
    os.system(f'cp testing/files/004_祝！！！.jpg {tmp_path}')

    assert files.dir_not_empty(data) is False

    # Copy all images to dir
    for f in ('008_77803142_p0.png', '017_ミコニャン.jpg'):
        os.system(f'cp testing/files/{f} {tmp_path}')

    assert files.dir_not_empty(data)

    # Test Throw some errors
    class FakeData:
        def __init__(self):
            self.download_path = Path('testing/files/')

        @property
        def first_img(self):
            raise KeyError

    data = FakeData()
    assert files.dir_not_empty(data)

    class FakeData:
        def __init__(self):
            self.download_path = Path('testing/files/')

        @property
        def first_img(self):
            raise AttributeError

    data = FakeData()
    assert files.dir_not_empty(data)
