import curses
from unittest.mock import Mock

import pytest

from pick import Picker

from koneko import picker, KONEKODIR
from koneko.picker import EMPTY_WARNING, EMPTY_FILTER_WARNING
from conftest import CustomExit, raises_customexit


@pytest.fixture
def patch_filter_history(monkeypatch):
    monkeypatch.setattr('koneko.files.filter_history', lambda x: ['actions'])

@pytest.mark.parametrize('letter', ('w', 's'))
def test_ws_picker(monkeypatch, letter):
    class FakePick(Picker):
        def run_loop(self):
            c = ord(letter)

            if c in self.custom_handlers:
                ret = self.custom_handlers[c](self)
                if ret:
                    return ret
                return self.get_selected()

    fakepicker = FakePick
    monkeypatch.setattr('koneko.picker.Picker', fakepicker)
    mypicker = picker.ws_picker(['1', '2'], 'title')
    mypicker.register_custom_handler(ord(letter), lambda x: x.move_up())
    try:
        assert mypicker.start() == ('2', 1)
    except curses.error:
        pass  # Github actions doesn't have a terminal


@pytest.mark.parametrize('letter', 'ybfdq')
def test_pick_dirs_picker(monkeypatch, letter):
    class FakePick(Picker):
        def run_loop(self):
            c = ord(letter)

            if c in self.custom_handlers:
                ret = self.custom_handlers[c](self)
                if ret:
                    return ret
                return self.get_selected()

    fakepicker = FakePick
    monkeypatch.setattr('koneko.picker.Picker', fakepicker)
    mypicker = picker._pick_dirs_picker(['1', '2'], 'title')
    mypicker.register_custom_handler(ord(letter), lambda p: (None, letter))
    try:
        assert mypicker.start() == (None, letter)
    except curses.error:
        pass  # Github actions doesn't have a terminal


def test_pick_dir_loop_y(monkeypatch, tmp_path):
    mocked = Mock()
    mocked.start = lambda: (None, 'y')
    monkeypatch.setattr('koneko.picker._pick_dirs_picker', lambda *a: mocked)
    monkeypatch.setattr('koneko.utils.quit_on_q', lambda x: False)
    monkeypatch.setattr('koneko.files.path_valid', lambda x: True)
    assert picker._pick_dir_loop(tmp_path, 'title', [2], ['2']) == tmp_path


def test_pick_dir_loop_c(monkeypatch, tmp_path):
    mocked = Mock()
    mocked.start = lambda: (None, 'c')
    monkeypatch.setattr('koneko.picker._pick_dirs_picker', lambda *a: mocked)
    monkeypatch.setattr('koneko.utils.quit_on_q', lambda x: False)
    monkeypatch.setattr('koneko.picker.handle_clear', raises_customexit)
    with pytest.raises(CustomExit):
        picker._pick_dir_loop(tmp_path, 'title', [2], ['2'])


def test_pick_dir_loop_int(monkeypatch, tmp_path):
    mocked = Mock()
    mocked.start = lambda: (None, 1)
    monkeypatch.setattr('koneko.picker._pick_dirs_picker', lambda *a: mocked)
    monkeypatch.setattr('koneko.utils.quit_on_q', lambda x: False)
    monkeypatch.setattr('koneko.picker.handle_cd', raises_customexit)
    with pytest.raises(CustomExit):
        picker._pick_dir_loop(tmp_path, 'title', [2, 2], ['2', '2'])


def test_lscat_app_main(monkeypatch):
    monkeypatch.setattr('koneko.picker.Picker.start', lambda x: (None, 1))
    assert picker.lscat_app_main() == 1


def test_frequent_modes_picker(monkeypatch):
    monkeypatch.setattr('koneko.picker.Picker.start', lambda x: (None, 1))
    assert picker.frequent_modes_picker(['action']) == 1


def test_multiselect_picker(monkeypatch):
    monkeypatch.setattr('koneko.picker.Picker.start', lambda x: [(None, 1), (None, 2)])
    assert picker._multiselect_picker(['actions'], 'title', to_str=True) == ['2', '3']
    assert picker._multiselect_picker(['actions'], 'title', to_str=False) == [2, 3]


def test_select_modes_filter(monkeypatch):
    monkeypatch.setattr('koneko.picker.Picker.start', lambda x: [(None, 1), (None, 2)])
    assert picker.select_modes_filter(more=False) == ['2', '3']
    assert picker.select_modes_filter(more=True) == ['2', '3']


def test_ask_assistant(monkeypatch):
    monkeypatch.setattr('koneko.picker.Picker.start', lambda x: [(None, 1), (None, 2)])
    assert picker.ask_assistant() == [2, 3]


def test_pick_dir_y(monkeypatch, patch_filter_history):
    # Just to test the branch is reachable
    monkeypatch.setattr('koneko.picker.Picker.start', lambda x: (None, 'y'))
    monkeypatch.setattr('koneko.picker.actions_from_dir', raises_customexit)
    with pytest.raises(CustomExit):
        picker.pick_dir()


def test_pick_dir_b(monkeypatch, patch_filter_history):
    # Just to test the branch is reachable
    monkeypatch.setattr('koneko.picker.Picker.start', lambda x: (None, 'b'))
    monkeypatch.setattr('koneko.picker.actions_from_dir', raises_customexit)
    with pytest.raises(CustomExit):
        picker.pick_dir()

def test_pick_dir_d(monkeypatch, patch_filter_history, capsys):
    # Just to test the branch is reachable
    monkeypatch.setattr('koneko.picker.Picker.start', lambda x: (None, 'd'))
    monkeypatch.setattr('koneko.picker.actions_from_dir', raises_customexit)
    monkeypatch.setattr('builtins.input', lambda x: 'n')
    with pytest.raises(CustomExit):
        picker.pick_dir()
    captured = capsys.readouterr()
    assert captured.out == f'Are you sure you want to delete {KONEKODIR}?\n'


def test_pick_dir_f(monkeypatch, patch_filter_history):
    # Just to test the branch is reachable
    monkeypatch.setattr('koneko.picker.Picker.start', lambda x: (None, 'f'))
    monkeypatch.setattr('koneko.picker.handle_filter', raises_customexit)
    with pytest.raises(CustomExit):
        picker.pick_dir()


def test_handle_back():
    assert picker.handle_back(KONEKODIR) == KONEKODIR
    assert picker.handle_back(KONEKODIR / '1234') == KONEKODIR


def test_handle_delete(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr('builtins.input', lambda x: 'n')
    assert picker.handle_delete(tmp_path) == tmp_path
    assert tmp_path.is_dir()

    monkeypatch.setattr('builtins.input', lambda x: 'y')
    assert picker.handle_delete(tmp_path) == tmp_path.parent
    assert not tmp_path.is_dir()
    captured = capsys.readouterr()
    assert captured.out == f'Are you sure you want to delete {tmp_path}?\n' * 2


def test_handle_filter_clear(monkeypatch, tmp_path):
    monkeypatch.setattr('koneko.picker.select_modes_filter', lambda x: ['6'])
    assert picker.handle_filter(tmp_path, 'title') == ('title', [], ['6'])


@pytest.mark.parametrize('number', (str(x) for x in range(1, 6)))
def test_handle_filter(monkeypatch, tmp_path, number):
    monkeypatch.setattr('koneko.picker.select_modes_filter', lambda x: [number])
    monkeypatch.setattr('koneko.picker.try_filter_dir', lambda x: ['dirs'])
    assert (picker.handle_filter(tmp_path, 'title')
            == (f"Filtering modes=['{number}']\ntitle", ['dirs'], [number]))

def test_handle_cd_empty():
    assert picker.handle_cd(None, EMPTY_FILTER_WARNING, []) == (KONEKODIR, [])


def test_handle_cd_path_not_dir(tmp_path):
    assert picker.handle_cd(tmp_path, 'dir', ['modes']) == (tmp_path, ['modes'])


def test_handle_cd_path_is_dir(tmp_path):
    realpath = tmp_path / '1234'
    realpath.mkdir()
    assert picker.handle_cd(tmp_path, '1234', ['modes']) == (realpath, ['modes'])


def test_handle_clear_quit(monkeypatch):
    monkeypatch.setattr('koneko.picker.sys.exit', raises_customexit)
    monkeypatch.setattr('koneko.screens.clear_cache_loop', lambda: True)
    with pytest.raises(CustomExit):
        picker.handle_clear()

def test_handle_no_quit(monkeypatch):
    monkeypatch.setattr('koneko.screens.clear_cache_loop', lambda: False)
    picker.handle_clear()


def test_actions_from_dir_filter_inactive(monkeypatch):
    monkeypatch.setattr('koneko.files.filter_history', lambda x: 'sentinel')
    assert picker.actions_from_dir('not_konekodir', []) == 'sentinel'


def test_actions_from_dir_filter_inactive_empty(monkeypatch):
    monkeypatch.setattr('koneko.files.filter_history', lambda x: [])
    assert picker.actions_from_dir('not_konekodir', []) == [EMPTY_WARNING]


def test_actions_from_dir_filter_active(monkeypatch):
    monkeypatch.setattr('koneko.picker.try_filter_dir', lambda x: 'sentinel')
    assert picker.actions_from_dir(KONEKODIR, 'modes_is_not_none') == 'sentinel'


def test_actions_from_dir_mode2_success(monkeypatch):
    assert picker.actions_from_dir(KONEKODIR / '123', ['2']) == ['individual']


def test_actions_from_dir_mode2_mode1_fail(monkeypatch):
    monkeypatch.setattr('koneko.files.filter_history', lambda x: 'sentinel')
    assert picker.actions_from_dir(KONEKODIR / '123', ['2', '1']) == 'sentinel'


def test_actions_from_dir_mode2_individual_fail(monkeypatch):
    monkeypatch.setattr('koneko.files.filter_history', lambda x: 'sentinel')
    assert picker.actions_from_dir(KONEKODIR / '123' / 'individual', ['2']) == 'sentinel'

def test_actions_from_dir_mode2_path_notdigit_fail(monkeypatch):
    monkeypatch.setattr('koneko.files.filter_history', lambda x: 'sentinel')
    assert picker.actions_from_dir(KONEKODIR / 'notdigit', ['2']) == 'sentinel'


def test_try_filter_dir_sorted(monkeypatch):
    monkeypatch.setattr('koneko.files.filter_dir', lambda x: x)
    assert picker.try_filter_dir('hi') == sorted('hi')


def test_try_filter_dir_empty(monkeypatch):
    monkeypatch.setattr('koneko.files.filter_dir', lambda x: [])
    assert picker.try_filter_dir('hi') == [EMPTY_FILTER_WARNING]

