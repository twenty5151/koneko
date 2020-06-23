import os
import sys
import time
from pathlib import Path

from pixcat import Image
from blessed import Terminal

from koneko import KONEKODIR, lscat, config


term = Terminal()

def move_cursor_up(num):
    print(f'\033[{num}A', end='', flush=True)

def move_cursor_down(num=1):
    print(f'\033[{num}B', end='', flush=True)

def erase_line():
    print('\033[K', end='', flush=True)

def print_cols(spacing, ncols):
    for (idx, space) in enumerate(spacing[:ncols]):
        print(' ' * int(space), end='', flush=True)
        print(idx + 1, end='', flush=True)

def line_width(spacing, ncols):
    return sum(spacing) + ncols

class FakeData:
    def __init__(self, path):
        self.download_path = path

    @classmethod
    def gallery(cls):
        return cls(KONEKODIR / 'testgallery')

    @classmethod
    def user(cls):
        # Make sure it has a .koneko file
        return cls(KONEKODIR / 'testuser')

def display_user_row(thumbnail_size, preview_xcoords, padding):
    Image(
        KONEKODIR.parent / 'pics' / '71471144_p0.png'
    ).thumbnail(thumbnail_size).show(align='left', x=padding)

    for px in preview_xcoords:
        Image(
            KONEKODIR.parent / 'pics' / '71471144_p0.png'
        ).thumbnail(thumbnail_size).show(align='left', x=px, y=0)


def print_info(message_xcoord):
    print(' ' * message_xcoord, '000', '\n',
          ' ' * message_xcoord, 'Example artist', sep='')


def show_single(x, thumbnail_size):
    img = Image(
        KONEKODIR.parent / 'pics' / '71471144_p0.png'
    ).thumbnail(thumbnail_size)
    img.show(align='left', x=x, y=0)
    return img


def main():
    os.system('clear')
    print(*('Welcome to the lscat interactive script',
        '1. Launch koneko configuration assistance',
        '2. Display KONEKODIR / testgallery',
        '3. Display KONEKODIR / testuser',
        '4. Browse a cached dir to display',
        '5. Display a specified path'), sep='\n')

    ans = input('\nPlease select an action: ')
    print('')

    case = {
        '1': config_assistance,
        '2': display_gallery,
        '3': display_user,
        '4': browse_cache,
        '5': display_path
    }

    func = case.get(ans, None)
    if func:
        func()
    else:
        print('Invalid command! Exiting...')


def display_gallery():
    data = FakeData.gallery()
    lscat.show_instant(lscat.TrackDownloads, data, True)

def display_user():
    data = FakeData.user()
    lscat.show_instant(lscat.TrackDownloadsUsers, data)

def display_path():
    path = input('Please paste in your path:\n')
    if not Path(path).is_dir():
        print('Invalid path!')
        return

    data = FakeData(path)
    lscat.show_instant(lscat.TrackDownloads, data, True)


def browse_cache():
    path = pick_dir()
    data = FakeData(path)

    ans = input('Does this directory have a .koneko file? [y/N] ')

    if ans == 'n':
        lscat.show_instant(lscat.TrackDownloads, data, True)
    else:
        lscat.show_instant(lscat.TrackDownloadsUsers, data)

def pick_dir():
    path = KONEKODIR

    while True:
        files = sorted(os.listdir(path))
        for i, f in enumerate(files):
            print(i, '--', f)

        print('\nSelect a directory to view (enter its index)')
        print('If you want to display this directory, enter "y"')
        ans = input()

        if ans == 'q':
            sys.exit(0)

        elif ans == 'y':
            return path

        elif ans == 'b':
            path = path.parent
            continue

        path = path / files[int(ans)]



def config_assistance():
    print(*('\n=== Configuration assistance ===',
        'Please select an action index',
        '1. Thumbnail size',
        'A. x-padding',
        'B. y-padding',
        '2. Number of columns',
        'C. Number of rows',
        '3. Page spacing',
        '4. Gallery print spacing',
        '5. User mode print info x-position',
        'a. (Run all of the above)\n'), sep='\n')
    ans = input()

    if ans in {'1', 'a'}:
        size = thumbnail_size_assistant()
    else:
        size = config.thumbnail_size_config()

    if ans in {'A', 'a'}:
        xpadding = xpadding_assistant(size)

    if ans in {'2', 'a'}:
        ncols = ncols_assistant(size)

    if ans in {'3', 'a'}:
        page_spacing = page_spacing_assistant(size)

    if ans in {'4', 'a'}:
        gallery_print_spacing = gallery_print_spacing_assistant()

    if ans in {'5', 'a'}:
        user_info_xcoord = user_print_name_spacing_assistant(size)


    print('\nYour recommended settings are:')
    if ans in {'1', 'a'}:
        print(f'image_thumbnail_size = {size}')

    if ans in {'A', 'a'}:
        print(f'images_x_spacing = {xpadding}')

    if ans in {'2', 'a'}:
        print(f'number_of_columns = {ncols}')

    if ans in {'3', 'a'}:
        print(f'page_spacing = {page_spacing}')

    if ans in {'4', 'a'}:
        print(f'gallery_print_spacing =',
              ','.join((str(x) for x in gallery_print_spacing)))

    if ans in {'5', 'a'}:
        print(f'users_print_name_xcoord = {user_info_xcoord}')

    input('\nEnter any key to quit\n')


def print_thumbnail_help():
    os.system('clear')
    bottom = term.height - 7
    move_cursor_down(bottom)
    print(*('=== Thumbnail size ===',
        'This will display an image whose thumbnail size can be varied',
        'Use +/= to increase the size, and -/_ to decrease it',
        'Use q to exit the program, and press enter to confirm the size',
        '\nKeep in mind this size will be used for a grid of images'),
        sep='\n')

def thumbnail_size_assistant():
    print_thumbnail_help()

    image = Image(
        KONEKODIR.parent / 'pics' / '71471144_p0.png'
    )

    size = 300  # starting size
    with term.cbreak():
        while True:
            image.thumbnail(size).show(align='left', x=0, y=0)

            ans = term.inkey()

            if ans in {'+', '='}:
                size += 20

            elif ans in {'-', '_'}:
                image.hide()
                size -= 20

            elif ans == 'q':
                sys.exit(0)

            elif ans.code == 343:  # Enter
                return size

            #elif ans == 't':
            # TODO: preview a grid with chosen size


def xpadding_assistant(thumbnail_size):
    print('\n=== Image x spacing ===')
    print('1) Move the second image so that it is just to the right of the first image')
    print('Use +/= to move it to the right, and -/_ to move it to the left.\n'
          'Press enter to confirm')
    print('2) Based on the position of the second image, adjust its position to suit you.\n'
          'This value will be the x spacing')
    print('\nUse q to exit the program, and press enter to go to the next assistant\n')

    input('\nEnter any key to continue\n')
    os.system('clear')

    show_single(config.xcoords_config()[0], thumbnail_size)

    image_width, image = find_image_width(thumbnail_size)

    spaces = 0
    while True:
        with term.cbreak():
            # erase_line() doesn't work here
            print('\r' + ' ' * 20, end='', flush=True)
            print('\r', end='', flush=True)
            print(f'x spacing = {spaces}', end='', flush=True)

            ans = term.inkey()

            if ans == 'q':
                sys.exit(0)

            elif ans.code == 343:  # Enter
                return spaces

            elif spaces >= 0:
                image.hide()
                move_cursor_up(1)

            if ans in {'+', '='}:
                spaces += 1

            elif ans in {'-', '_'} and spaces > 0:
                spaces -= 1

            image = show_single(image_width + spaces, thumbnail_size)


def find_image_width(thumbnail_size):
    image = None
    spaces = 0
    valid = True

    while True:
        with term.cbreak():
            if valid:
                erase_line()
                print(f'image width = {spaces}', end='', flush=True)

            ans = term.inkey()

            if ans == 'q':
                sys.exit(0)

            elif ans.code == 343:  # Enter
                erase_line()
                return spaces, image

            elif spaces > 0 and image:
                image.hide()
                move_cursor_up(1)

            if ans in {'+', '='}:
                spaces += 1

            elif ans in {'-', '_'} and spaces > 0:
                spaces -= 1

            else:
                valid = False
                continue

            image = show_single(spaces, thumbnail_size)
            valid = True


def ncols_assistant(thumbnail_size):
    print('\n=== Number of columns ===')
    print('Use +/= to show another column, and -/_ to hide the rightmost column')
    print('Increase the number of columns just until no more can fit in your screen')
    print('Use q to exit the program, and press enter to go to the next assistant\n')

    input('\nEnter any key to continue\n')
    os.system('clear')

    xcoords = config.xcoords_config() * 2

    show_single(xcoords[0], thumbnail_size)

    images = []  # LIFO stack
    i = 0  # Zero index to make indexing `images` easier
    while True:
        with term.cbreak():
            erase_line()
            print(f'Number of columns = {i + 1}', end='', flush=True)

            ans = term.inkey()

            if ans in {'+', '='}:
                images.append(show_single(xcoords[i + 1], thumbnail_size))
                i += 1

            elif ans in {'-', '_'} and images:
                i -= 1
                images[i].hide()
                images.pop(i)
                move_cursor_up(1)

            elif ans == 'q':
                sys.exit(0)

            elif ans.code == 343:  # Enter
                print('')
                return i + 1  # Zero index


def page_spacing_assistant(thumbnail_size):
    print('\n=== Page spacing ===')
    print('This will display an image, then print newlines.')
    print('Your desired setting is the number when '
          'the image completely scrolls out of view')

    input('Enter any key to continue\n')
    os.system('clear')

    Image(
        KONEKODIR.parent / 'pics' / '71471144_p0.png'
    ).thumbnail(thumbnail_size).show(align='left')

    time.sleep(0.5)

    for i in range(term.height + 5):
        print(i)
        time.sleep(0.1)

    print('When the image just completely scrolls out of view, '
          'what is the largest number?')
    print('(By default on kitty, ctrl+shift+up/down '
          'scrolls up/down a line)')
    return input()


def gallery_print_spacing_assistant():
    print('\n=== Gallery print spacing ===')
    print('Print spacing is the number of blank spaces between each number')
    print('For example:')
    print('x' * 9, '1', 'x' * 17, '2', 'x' * 17, '3', '...', sep='')

    print('\nUse +/= to increase the spacing, and -/_ to decrease it')
    print('Use q to exit the program, and press enter to go to the next assistant\n')
    print('Use left and right arrow keys to change the current space selection')

    print('\nPick a directory to preview in grid first')

    input('\nEnter any key to continue\n')
    os.system('clear')

    path = pick_dir()
    data = FakeData(path)
    lscat.show_instant(lscat.TrackDownloads, data)
    print('\n')

    ncols = config.ncols_config()
    spacing = [9, 17, 17, 17, 17] + [17] * (ncols - 5)
    current_selection = 0

    while True:
        with term.cbreak():
            move_cursor_up(2)
            erase_line()
            print_cols(spacing, ncols)
            erase_line()
            print(f'\nAdjusting number {current_selection+1}', flush=True)

            ans = term.inkey()

            if ans in {'+', '='}:
                new = int(spacing[current_selection]) + 1
                if line_width(spacing, ncols) < term.width:
                    spacing[current_selection] = new

            elif ans in {'-', '_'}:
                spacing[current_selection] = int(spacing[current_selection]) - 1
                if spacing[current_selection] < 0:
                    spacing[current_selection] = 0

            # right arrow
            elif ans.code == 261 or ans in {'d', 'l'}:
                current_selection += 1
                if current_selection >= len(spacing):
                    current_selection -= 1

            # left arrow
            elif ans.code == 260 or ans in {'a', 'h'}:
                if current_selection > 0:
                    current_selection -= 1

            elif ans == 'q':
                sys.exit(0)

            elif ans.code == 343:  # Enter
                return spacing


def user_print_name_spacing_assistant(thumbnail_size):
    print('\n=== User print name xcoord ===')
    print('This will display an image, then print a sample index and artist name.')
    print('\nUse +/= to move the text right, and -/_ to move it left')
    print('Adjust the position as you see fit')
    print('Use q to exit the program, and press enter to confirm the current position')

    input('\nEnter any key to continue\n')
    os.system('clear')

    spacing, padding = config.get_gen_users_settings()
    preview_xcoords = config.xcoords_config(offset=1)[-3:]

    display_user_row(thumbnail_size, preview_xcoords, padding)
    move_cursor_up(5)

    while True:
        with term.cbreak():
            erase_line()         # Erase the first line
            move_cursor_down()   # Go down and erase the second line
            erase_line()
            move_cursor_up(1)    # Go back up to the original position
            print_info(spacing)  # Print info takes up 2 lines
            move_cursor_up(2)    # so go back to the top

            ans = term.inkey()

            if ans in {'+', '='}:
                spacing += 1

            elif ans in {'-', '_'}:
                if spacing > 0:
                    spacing -= 1

            elif ans == 'q':
                sys.exit(0)

            elif ans.code == 343:  # Enter
                print('\n' * 3)
                return spacing

