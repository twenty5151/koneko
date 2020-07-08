import os
from pathlib import Path
from collections import namedtuple

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


@pytest.mark.parametrize('mkdir', (True, False))
def test_remove_dir_if_exist(tmp_path, mkdir):
    path = tmp_path / 'test'
    if mkdir:
        path.mkdir()
    FakeData = namedtuple('data', ('download_path',))
    data = FakeData(path)
    files.remove_dir_if_exist(data)
    assert not path.is_dir()


def test_filter_history(tmp_path):
    (tmp_path / 'history').touch()
    assert files.filter_history(tmp_path) == []


def data_faker(tmp_path):
    FakeData = namedtuple('data', ('download_path', 'first_img', 'all_names'))
    data = FakeData(
        tmp_path, "004_祝！！！.jpg",
        ["004_祝！！！.jpg", '008_77803142_p0.png', '017_ミコニャン.jpg']
    )
    return data

def test_dir_not_empty_dir_exists_but_empty(tmp_path):
    """Test dir exists but is empty"""
    data = data_faker(tmp_path)
    tmp_path.mkdir(exist_ok=True)
    assert files.dir_not_empty(data) is False

def test_dir_not_empty_incomplete_dir(tmp_path):
    data = data_faker(tmp_path)
    # Copy .koneko and only one image to that dir
    (tmp_path / '.koneko').touch()
    os.system(f'cp testing/files/004_祝！！！.jpg {tmp_path}')

    assert files.dir_not_empty(data) is False

def test_dir_not_empty_all_images_present(tmp_path):
    data = data_faker(tmp_path)
    # Copy all images to dir
    for f in data.all_names:
        os.system(f'cp testing/files/{f} {tmp_path}')

    assert files.dir_not_empty(data)

@pytest.mark.parametrize('error', (KeyError, AttributeError))
def test_dir_not_empty_errors_return_true(tmp_path, error):
    class FakeData:
        def __init__(self):
            self.download_path = Path('testing/files/')

        @property
        def first_img(self):
            raise error

    data = FakeData()
    assert files.dir_not_empty(data)


def test_filter_dir_1(monkeypatch, tmp_path):
    monkeypatch.setattr('koneko.files.KONEKODIR', tmp_path)
    (tmp_path / '1234').touch()
    (tmp_path / 'testgallery').touch()
    (tmp_path / 'notanumber').touch()

    assert set(files.filter_dir(['1'])) == {'testgallery', '1234'}


def test_filter_dir_2(monkeypatch, tmp_path):
    monkeypatch.setattr('koneko.files.KONEKODIR', tmp_path)
    (tmp_path / '1234').mkdir()
    (tmp_path / '1234' / 'individual').touch()
    (tmp_path / '5678').mkdir()
    (tmp_path / 'testgallery').touch()
    (tmp_path / 'notanumber').touch()

    assert files.filter_dir(['2']) == ['1234']


def test_filter_dir_3(monkeypatch, tmp_path):
    monkeypatch.setattr('koneko.files.KONEKODIR', tmp_path)
    (tmp_path / '1234').touch()
    (tmp_path / 'testuser').touch()
    (tmp_path / 'following').touch()

    assert set(files.filter_dir(['3'])) == {'following', 'testuser'}


def test_filter_dir_4(monkeypatch, tmp_path):
    monkeypatch.setattr('koneko.files.KONEKODIR', tmp_path)
    (tmp_path / '1234').touch()
    (tmp_path / 'search').touch()
    (tmp_path / 'notanumber').touch()

    assert files.filter_dir(['4']) == ['search']

def test_filter_dir_5(monkeypatch, tmp_path):
    monkeypatch.setattr('koneko.files.KONEKODIR', tmp_path)
    (tmp_path / '1234').touch()
    (tmp_path / 'illustfollow').touch()
    (tmp_path / 'notanumber').touch()

    assert files.filter_dir(['5']) == ['illustfollow']