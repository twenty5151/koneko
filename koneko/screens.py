import os
import shutil

import pixcat

from koneko import (
    ui,
    cli,
    utils,
    config,
    lscat,
    KONEKODIR,
    __version__,
    WELCOME_IMAGE
)


def display(path, icat_size, ueberzug_size):
    if config.use_ueberzug():
        return lscat.ueberzug_display(path, 0, 0, ueberzug_size // 20)
    pixcat.Image(path).thumbnail(icat_size).show(align='left', y=0)
    return None


def begin_prompt(printmessage=True) -> 'IO[str]':
    messages = (
        '',
        f'Welcome to koneko v{__version__}\n',
        'Select an action:',
        '1. View artist illustrations',
        '2. Open pixiv post',
        '3. View following artists',
        '4. Search for artists',
        '5. View illustrations of all following artists',
        '6. View recommended illustrations',
        'f. Frequent modes and user inputs', '',
        '?. Info',
        'm. Manual',
        'b. Browse cache (offline)',
        'q. Quit',
    )
    if printmessage:
        for message in messages:
            print(' ' * 30, message)

    canvas = display(WELCOME_IMAGE, 600, 600)

    command = input('\n\nEnter a command: ')
    utils.exit_if_exist(canvas)
    return command


@utils.catch_ctrl_c
def show_man_loop() -> 'IO':
    os.system('clear')
    print(cli.__doc__)
    print(' ' * 3, '=' * 30)
    print(ui.ArtistGallery.__doc__)
    print(' ' * 3, '=' * 30)
    print(ui.Image.__doc__)
    print(' ' * 3, '=' * 30)
    print(ui.AbstractUsers.__doc__)
    print(' ' * 3, '=' * 30)
    print(ui.IllustFollowGallery.__doc__)
    while True:
        help_command = input('\n\nEnter any key to return: ')
        if help_command or help_command == '':
            os.system('clear')
            break


@utils.catch_ctrl_c
def clear_cache_loop() -> 'IO[bool]':
    print('Do you want to remove all cached images?')
    print('This will not remove images you explicitly downloaded to ~/Downloads.')
    print(f'Directory to be deleted: {KONEKODIR}')
    while True:
        help_command = input('\nEnter y to confirm: ')
        if help_command == 'y':
            shutil.rmtree(KONEKODIR)
            os.system('clear')
            return True
        else:
            print('Operation aborted!')
            os.system('clear')
            return False


@utils.catch_ctrl_c
def info_screen_loop() -> 'IO':
    os.system('clear')
    messages = (
        '',
        f'koneko こねこ version {__version__} beta\n',
        "Browse pixiv in the terminal using kitty's icat to display",
        'images with images embedded in the terminal\n',
        "1. View an artist's illustrations",
        '2. View a post (support multiple images)',
        '3. View artists you followed',
        '4. Search for artists and browse their works.',
        '5. View latest illustrations from artist you follow.\n',
        'Thank you for using koneko!',
        'Please star, report bugs and contribute in:',
        'https://github.com/twenty5151/koneko',
        'GPLv3 licensed\n',
        'Credits to amasyrup (甘城なつき):',
        'Welcome image: https://www.pixiv.net/en/artworks/71471144',
        'Current image: https://www.pixiv.net/en/artworks/79494300',
    )

    for message in messages:
        print(' ' * 26, message)

    canvas = display(KONEKODIR.parent / 'pics' / '79494300_p0.png', 750, 500)

    while True:
        help_command = input('\nEnter any key to return: ')
        if help_command or help_command == '':
            os.system('clear')
            utils.exit_if_exist(canvas)
            break
