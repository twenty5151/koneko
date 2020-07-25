import os
import sys
import random
from pathlib import Path
from unittest.mock import Mock, call
from collections import namedtuple

import pytest

from koneko import lscat, pure
from conftest import setup_test_config


FakeData = namedtuple('data', ('download_path',))


def test_icat(monkeypatch):
    mocked_pixcat = Mock()
    monkeypatch.setattr('koneko.lscat.Image', lambda *a, **k: mocked_pixcat)
    try:
        lscat.icat('./testing/files/004_祝！！！.jpg')
    except OSError:
        # Github doesn't connect to terminal
        return True
    assert mocked_pixcat.mock_calls == mocked_pixcat.method_calls == [call.show()]


def test_show_instant(monkeypatch, tmp_path, use_test_cfg_path):
    showed = []

    class FakeTracker:
        def __init__(self, data):
            pass

        def update(self, new):
            showed.append(new)

    FakeData = namedtuple('data', ('download_path',))

    # This config has print_info = True
    setup_test_config(tmp_path)

    fakedata = FakeData(Path('testing/files/'))
    lscat.show_instant(FakeTracker, fakedata)
    assert set(showed) == {
        '004_祝！！！.jpg', 'mode3.json',
        'mode1.json', 'not_an_image.txt', '008_77803142_p0.png',
        '017_ミコニャン.jpg', 'mode2.json'
    }


def test_TrackDownloads(monkeypatch):
    mocked_data = Mock()
    mocked_generator = Mock()
    tracker = lscat.TrackDownloads(mocked_data)
    tracker.generator = mocked_generator

    correct_order = list(range(30))
    test_pics = [f"{str(idx).rjust(3, '0')}_test"
                 for idx in list(range(30))]

    # Shuffle list of pics
    for pic in random.sample(test_pics, 30):
        tracker.update(pic)

    assert len(mocked_generator.mock_calls) == 30
    methods_called = [mocked_generator.mock_calls[i][0] for i in range(30)]
    # Only thing the tracker does is to call send() on the generator
    assert methods_called == ['send'] * 30

    #         first value in tuple (eg '020_test') <--|
    #                                                 |  |--> convert digits to int
    #  arg passed into generator.send, is tuple <--|  |  |
    #                                              |  |  |
    sent_img = [int(mocked_generator.mock_calls[i][1][0][:3]) for i in range(30)]
    assert correct_order == sent_img


def test_TrackDownloadsUser(monkeypatch):
    mocked_data = Mock()
    mocked_data.splitpoint = 30
    mocked_generator = Mock()
    tracker = lscat.TrackDownloadsUsers(mocked_data)
    tracker.generator = mocked_generator

    correct_order = pure.generate_orders(120, 30)
    test_pics = [f"{str(idx).rjust(3, '0')}_test"
                 for idx in list(range(120))]

    # Shuffle list of pics
    for pic in random.sample(test_pics, 120):
        tracker.update(pic)

    assert len(mocked_generator.mock_calls) == 120
    methods_called = [mocked_generator.mock_calls[i][0] for i in range(120)]
    # Only thing the tracker does is to call send() on the generator
    assert methods_called == ['send'] * 120

    #         first value in tuple (eg '020_test') <--|
    #                                                 |  |--> convert digits to int
    #  arg passed into generator.send, is tuple <--|  |  |
    #                                              |  |  |
    sent_img = [int(mocked_generator.mock_calls[i][1][0][:3]) for i in range(120)]
    assert correct_order == sent_img


def test_TrackDownloadsUser2(monkeypatch, tmp_path, use_test_cfg_path):
    """Test with .koneko file"""
    setup_test_config(tmp_path)

    data = FakeData(Path('testing/files/user'))
    data.download_path.mkdir()
    pics = ('004_祝！！！.jpg', '017_ミコニャン.jpg', '008_77803142_p0.png')
    for pic in pics:
        os.system(f'cp testing/files/{pic} testing/files/user/')

    os.system('touch testing/files/user/.koneko')
    with open('testing/files/user/.koneko', 'w') as f:
        f.write('3')

    lscat.show_instant(lscat.TrackDownloadsUsers, data)

    tracker = lscat.TrackDownloadsUsers(data)
    for pic in pics:
        tracker.update(pic)

    os.system(f'rm -r {data.download_path}')


def test_TrackDownloadsImage(monkeypatch):
    mocked_data = Mock()
    mocked_generator = Mock()
    mocked_data.page_num = 0
    tracker = lscat.TrackDownloadsImage(mocked_data)
    tracker.generator = mocked_generator

    correct_order = list(range(10))
    test_pics = [f"12345_p{idx}_master1200.jpg"
                 for idx in list(range(10))]

    # No need to shuffle because updates are always in order
    for pic in test_pics:
        tracker.update(pic)

    assert len(mocked_generator.mock_calls) == 10
    mock_calls = [call.send(f'12345_p{i}_master1200.jpg') for i in range(0, 10)]
    assert mocked_generator.mock_calls == mock_calls


def test_generate_page(monkeypatch, capsys):
    mocked_pixcat = Mock()
    monkeypatch.setattr('koneko.lscat.Image', lambda *a, **k: mocked_pixcat)
    monkeypatch.setattr('koneko.Terminal.width', 100)
    monkeypatch.setattr('koneko.Terminal.height', 20)
    monkeypatch.setattr('koneko.config.gallery_page_spacing_config', lambda: 1)

    test_pics = [f"{str(idx).rjust(3, '0')}_test"
                 for idx in list(range(30))]

    gen = lscat.generate_page(Path('.'))  # Path doesn't matter
    gen.send(None)

    # No need to shuffle, tracker already shuffles
    for pic in test_pics:
        gen.send(pic)

    # One for .thumbnail() and one for .show(), so total is 30+30
    thumb_calls = [x for x in mocked_pixcat.mock_calls if x[1]]
    thumb_calls_args = [x[1] for x in thumb_calls]
    assert len(mocked_pixcat.mock_calls) == 60  # 30 images * 2 because thumbnail + show == twice
    assert len(thumb_calls) == 30  # 30 images
    # Default thumbnail size
    assert thumb_calls_args == [(310,)] * 30

    show_calls = [x for x in mocked_pixcat.mock_calls if not x[1]]
    kwargs = [x[2] for x in show_calls]
    align = [x['align'] for x in kwargs]
    xcoords = [x['x'] for x in kwargs]
    ycoords = [x['y'] for x in kwargs]
    assert align == ['left'] * 30  # 30 images
    # Len of lists == 30 images
    assert xcoords == [2, 20, 38, 56, 74] * 6
    assert ycoords == [0, 0, 0, 0, 0, 9, 9, 9, 9, 9] * 3

    captured = capsys.readouterr()
    assert captured.out == '\n\n\n\n'


def test_generate_users(monkeypatch, capsys):
    mocked_pixcat = Mock()
    monkeypatch.setattr('koneko.lscat.Image', lambda *a, **k: mocked_pixcat)
    monkeypatch.setattr('koneko.Terminal.width', 100)
    monkeypatch.setattr('koneko.Terminal.height', 20)
    monkeypatch.setattr('koneko.config.users_page_spacing_config', lambda: 1)

    test_pics = [f"{str(idx).rjust(3, '0')}_test"
                 for idx in list(range(120))]

    gen = lscat.generate_users(Path('.'))  # Path doesn't matter
    gen.send(None)

    # No need to shuffle, tracker already shuffles
    for pic in test_pics:
        gen.send(pic)

    # One for .thumbnail() and one for .show(), so total is 30+30
    thumb_calls = [x for x in mocked_pixcat.mock_calls if x[1]]
    thumb_calls_args = [x[1] for x in thumb_calls]
    assert len(mocked_pixcat.mock_calls) == 240  # 120 images * 2 because thumbnail + show == twice
    assert len(thumb_calls) == 120  # Number of images
    # Default thumbnail size
    assert thumb_calls_args == [(310,)] * 120

    show_calls = [x for x in mocked_pixcat.mock_calls if not x[1]]
    kwargs = [x[2] for x in show_calls]
    align = [x['align'] for x in kwargs]
    xcoords = [x['x'] for x in kwargs]
    ycoords = [x['y'] for x in kwargs]
    assert align == ['left'] * 120  # 120 images
    assert xcoords == [2, 39, 57, 75] * 30  # total len == 120
    assert ycoords == [0] * 120  # 120 images

    captured = capsys.readouterr()
    assert captured.out[0:100] == '                  00\n                  test\n\n\n                  04\n                  test\n\n\n        '

    assert captured.out[500:600] == 'est\n\n\n                  44\n                  test\n\n\n                  48\n                  test\n\n\n  '

    assert captured.out[:100] == '                  00\n                  test\n\n\n                  04\n                  test\n\n\n        '


def test_generate_previews(monkeypatch):
    mocked_pixcat = Mock()
    monkeypatch.setattr('koneko.lscat.Image', lambda *a, **k: mocked_pixcat)
    monkeypatch.setattr('koneko.Terminal.width', 100)
    monkeypatch.setattr('koneko.Terminal.height', 20)

    test_pics = [f"12345_p{idx}_master1200.jpg"
                 for idx in list(range(10))]

    gen = lscat.generate_previews(Path('.'), 10)  # Path doesn't matter
    gen.send(None)

    # No need to shuffle, tracker already shuffles
    for pic in test_pics:
        gen.send(pic)

    # One for .thumbnail() and one for .show(), so total is 30+30
    thumb_calls = [x for x in mocked_pixcat.mock_calls if x[1]]
    thumb_calls_args = [x[1] for x in thumb_calls]
    assert len(mocked_pixcat.mock_calls) == 20  # Ten images * 2 because thumbnail + show == twice
    assert len(thumb_calls) == 10  # Ten images
    # Default thumbnail size
    assert thumb_calls_args == [(310,)] * 10

    show_calls = [x for x in mocked_pixcat.mock_calls if not x[1]]
    kwargs = [x[2] for x in show_calls]
    align = [x['align'] for x in kwargs]
    xcoords = [x['x'] for x in kwargs]
    ycoords = [x['y'] for x in kwargs]
    assert align == ['left'] * 10  # Ten images
    assert xcoords == [2, 2] + [74] * 8  # Total len == 10
    assert ycoords == [0, 9] *  5  # Ten images

