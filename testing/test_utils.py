import os
import sys
from pathlib import Path

import pytest

from koneko import utils

# Lmao python
sys.path.append('testing')


def test_find_number_map(monkeypatch):
    monkeypatch.setattr('koneko.utils.ncols_config', lambda: 5)
    assert ([utils.find_number_map(x, y)
             for y in range(1, 7)
             for x in range(1, 6)] == list(range(30)))
    assert not utils.find_number_map(0, 100)

    monkeypatch.setattr('koneko.utils.ncols_config', lambda: 6)
    assert [utils.find_number_map(x, y)
            for y in range(1, 7)
            for x in range(1, 7)][:30] == list(range(30))

def test_cd():
    current_dir = os.getcwd()
    with utils.cd(current_dir):
        testdir = os.getcwd()

    assert testdir == os.getcwd()
    assert os.getcwd() == current_dir


def test_verify_full_download():
    assert utils.verify_full_download("testing/files/008_77803142_p0.png") == True
    assert utils.verify_full_download("testing/files/not_an_image.txt") == False
    # The above code will remove the file
    os.system("touch testing/files/not_an_image.txt")

def test_dir_not_empty():
    class FakeData:
        def __init__(self):
            self.download_path = Path('testing/files/')
            self.first_img = "004_祝！！！.jpg"

    # Assert current dir is not empty
    data = FakeData()
    assert utils.dir_not_empty(data)

    # Dir exists but is empty
    Path('testing/files/empty_dir').mkdir()
    data.download_path = Path('testing/files/empty_dir')
    assert utils.dir_not_empty(data) is False

    # .koneko in dir and first image in dir
    os.system('touch testing/files/empty_dir/.koneko')
    os.system('cp testing/files/004_祝！！！.jpg testing/files/empty_dir/')

    assert utils.dir_not_empty(data)

    os.system('rm -r testing/files/empty_dir')

    # Throw some errors
    class FakeData:
        def __init__(self):
            self.download_path = Path('testing/files/')

        @property
        def first_img(self):
            raise KeyError

    data = FakeData()
    assert utils.dir_not_empty(data)

    class FakeData:
        def __init__(self):
            self.download_path = Path('testing/files/')

        @property
        def first_img(self):
            raise AttributeError

    data = FakeData()
    assert utils.dir_not_empty(data)
