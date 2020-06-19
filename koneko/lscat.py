"""The default image renderer for koneko.

1) The ui classes start the download with the appropriate tracker instance.
   The tracker's update method acts as a callback upon a finished download
2) After each image finishes downloading, the callback is triggered (`tracker.update()`)
3) The `update()` method stores which images have finished downloading and their
   respective number, but has not been displayed yet.
4) On every callback, the `update()` method inspects the list against the given order.
   If the next image to be shown is in the list, it is displayed.
5) Immediately, remove the image from the lists and repeat the `_inspect()` method
   for the next valid image. If there is one, repeat. If not, do nothing and wait for
   more completed downloads
"""

import os
import threading
from abc import ABC

from pixcat import Image
from placeholder import m
from returns.result import safe

from koneko import utils, config


def ncols(term_width: int, img_width: int, padding: int) -> int:
    return round(term_width / (img_width + padding))

def xcoords(term_width: int, img_width=18, padding=2, offset=0) -> 'list[int]':
    """Generates the x-coord for each column to pass into pixcat
    If img_width == 18 and 90 > term_width > 110, there will be five columns,
    with spaces of (2, 20, 38, 56, 74)
    Meaning the first col has x-coordinates 2 and second col of 20
    """
    number_of_columns = ncols(term_width, img_width, padding)
    return [col % number_of_columns * img_width + padding + offset
            for col in range(number_of_columns)]

def ycoords(term_height: int, img_height=8, padding=1) -> 'list[int]':
    """Generates the y-coord for each row to pass into pixcat
    If img_height == 8 and 27 > term_height >= 18, there will be two rows,
    with spaces of (0, 9)
    Meaning the first row has y-coordinates 0 and second row of 9
    """
    number_of_rows = term_height // (img_height + padding)
    return [row * (img_height + padding)
            for row in range(number_of_rows)]


def icat(args: str) -> 'IO':
    os.system(f'kitty +kitten icat --silent {args}')

def show_instant(cls, data, gallerymode=False) -> 'IO':
    tracker = cls(data)
    # Filter out invisible files
    # (used to save splitpoint and total_imgs without requesting)
    _ = [tracker.update(x)
         for x in os.listdir(data.download_path)
         if not x.startswith('.')]

    if gallerymode and config.check_print_info():
        number_of_cols = config.ncols_config()

        spacing = config.get_settings('lscat', 'gallery_print_spacing').map(
                      m.split(',')
                  ).value_or((9, 17, 17, 17, 17))

        for (idx, space) in enumerate(spacing[:number_of_cols]):
            print(' ' * int(space), end='')
            print(idx + 1, end='')
        print('\n')


class AbstractTracker(ABC):
    def __init__(self):
        # Defined in child classes
        self.orders: 'list[int]'
        self.generator: 'generator[str]'

        self._lock = threading.Lock()
        self._downloaded: 'list[str]' = []
        self._numlist: 'list[int]' = []

        self.generator.send(None)

    def update(self, new: str) -> 'IO':
        # Can't use queues/channels instead of a lock, because of race conditions
        with self._lock:
            self._downloaded.append(new)
            self._numlist.append(int(new[:3]))

        self._inspect()

    def _inspect(self) -> 'IO':
        """Inspect the list of images that have finished downloading but not displayed
        yet. According to the given orders list, if the next image to be displayed
        is in the list, display it, then look for the next next image and repeat.
        """
        next_num = self.orders[0]

        if next_num in self._numlist:
            pic = self._downloaded[self._numlist.index(next_num)]
            self.generator.send(pic)

            self.orders = self.orders[1:]
            self._downloaded.remove(pic)
            self._numlist.remove(next_num)
            if self._downloaded and self.orders:
                self._inspect()

class TrackDownloads(AbstractTracker):
    """For gallery modes (1 & 5)"""
    def __init__(self, data):
        self.orders = list(range(30))
        self.generator = generate_page(data.download_path)
        super().__init__()

def read_invis(data) -> int:
    with utils.cd(data.download_path):
        with open('.koneko', 'r') as f:
            return int(f.read())

class TrackDownloadsUsers(AbstractTracker):
    """For user modes (3 & 4)"""
    def __init__(self, data):
        print_info = config.check_print_info()

        # Tries to access splitpoint attribute in the data instance
        # If it fails, `fix` it by calling the read_invis() function
        # Either way, the Success() result is inside the Result[] monad, so unwrap() it
        safe_func: 'func[Result[int]]' = safe(lambda x: data.splitpoint)
        splitpoint: int = safe_func().fix(lambda x: read_invis(data)).unwrap()

        # splitpoint == number of artists
        # Each artist has 3 previews, so the total number of pics is
        # splitpoint * 3 + splitpoint == splitpoint * 4
        self.orders = generate_orders(splitpoint * 4, splitpoint)

        self.generator = generate_users(data.download_path, print_info)
        super().__init__()

def generate_page(path) -> 'IO':
    """Given number, calculate its coordinates and display it, then yield"""
    left_shifts = config.xcoords_config()
    rowspaces = config.ycoords_config()
    number_of_cols = config.ncols_config()
    page_spacing = config.gallery_page_spacing_config()
    thumbnail_size = config.thumbnail_size_config()

    os.system('clear')
    while True:
        # Release control. When _inspect() sends another image,
        # assign to the variables and display it again
        image = yield

        number = int(image.split('_')[0])
        x = number % number_of_cols
        y = number // number_of_cols

        if number % 10 == 0 and number != 0:
            print('\n' * page_spacing)

        with utils.cd(path):
            Image(image).thumbnail(thumbnail_size).show(
                align='left', x=left_shifts[x], y=rowspaces[(y % 2)]
            )

def generate_users(path, print_info=True) -> 'IO':
    preview_xcoords = config.xcoords_config(offset=1)[-3:]
    message_xcoord, padding = config.get_gen_users_settings()
    page_spacing = config.users_page_spacing_config()
    thumbnail_size = config.thumbnail_size_config()

    os.system('clear')
    while True:
        # Wait for artist pic
        a_img = yield
        artist_name = a_img.split('.')[0].split('_')[-1]
        number = a_img.split('_')[0][1:]
        message = ''.join([number, '\n', ' ' * message_xcoord, artist_name])

        if print_info:  # Print the message (artist name)
            print(' ' * message_xcoord, message)
        print('\n' * page_spacing)  # Scroll to new 'page'

        with utils.cd(path):
            # Display artist profile pic
            Image(a_img).thumbnail(thumbnail_size).show(align='left', x=padding, y=0)

            # Display the three previews
            i = 0                   # Always resets for every artist
            while i < 3:            # Every artist has only 3 previews
                p_img = yield       # Wait for preview pic
                Image(p_img).thumbnail(thumbnail_size).show(align='left', y=0,
                                                            x=preview_xcoords[i])
                i += 1

def generate_orders(total_pics: int, artists_count: int) -> 'list[int]':
    """Returns the order of images to be displayed
    images 0-29 are artist profile pics
    images 30-119 are previews, 3 for each artist
    so the valid order is:
    0, 30, 31, 32, 1, 33, 34, 35, 2, 36, 37, 38, ...
    a, p,  p,  p,  a, p,  p,  p,  a, ...
    """
    artist = tuple(range(artists_count))
    prev = tuple(range(artists_count, total_pics))
    order = []
    a, p = 0, 0

    for i in range(total_pics):
        if i % 4 == 0:
            order.append(artist[a])
            a += 1
        else:
            order.append(prev[p])
            p += 1

    return order


class TrackDownloadsImage(AbstractTracker):
    """Experimental"""
    def __init__(self, data):
        self.orders = list(range(1, 30))
        self.generator = generate_previews(data.download_path)
        super().__init__(data)

    def update(self, new: str):
        """Overrides base class because numlist is different"""
        with self._lock:
            self._downloaded.append(new)
            self._numlist.append(int(f.split('_')[1].replace('p', '')))

        self._inspect()

def generate_previews(path) -> 'IO':
    """Experimental"""
    rowspaces = config.ycoords_config()
    left_shifts = config.xcoords_config()
    _xcoords = (left_shifts[0], left_shifts[-1])
    thumbnail_size = config.thumbnail_size_config()

    os.system('clear')
    i = 0
    while True:
        image = yield
        i += 1

        number = int(image.split('_')[1].replace('p', '')) - 1
        y = number % 2
        if i <= 2:
            x = 0
        else:
            x = 1

        with utils.cd(path):
            Image(image).thumbnail(thumbnail_size).show(
                align='left', x=_xcoords[x], y=rowspaces[y]
            )

if __name__ == '__main__':
    from koneko import KONEKODIR

    class FakeData:
        def __init__(self):
            # Either testuser or testgallery
            self.download_path = KONEKODIR / 'testgallery'

    data = FakeData()
    # Use whichever mode you pasted into the test dir
    # For Users, make sure it has a .koneko file
    #show_instant(TrackDownloadsUsers, data)
    show_instant(TrackDownloads, data)
