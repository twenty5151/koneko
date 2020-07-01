"""
Collection of functions that are pure and side effect free
Excluding printing, should not directly do any IO (file r/w, user input), including configs
Most input data come from impure sources (user input or network request), but this is allowed here
"""

import os
import re
from math import floor
from pathlib import Path

from placeholder import _
from funcy import curry, lmap
from returns.pipeline import flow

from koneko import colors as c


Map = curry(lmap)


def split_backslash_last(string: str) -> str:
    """Intended for splitting url to get filename, but it has lots of applications..."""
    return string.split('/')[-1]


def generate_filepath(filename: str) -> Path:
    return Path('~').expanduser() / 'Downloads' / filename


def prefix_filename(old_name_with_ext: str, new_name: str, number: int) -> str:
    """old_name_with_ext can be `test.png`, but new_name is `abcd`"""
    img_ext = old_name_with_ext.split('.')[-1]
    number_prefix = str(number).rjust(3, '0')
    new_file_name = f'{number_prefix}_{new_name}.{img_ext}'
    return new_file_name


def prefix_artist_name(name: str, number: int) -> str:
    number_prefix = str(number).rjust(2, '0')
    new_file_name = f"{number_prefix}\n{' ' * 19}{name}"
    return new_file_name


def print_multiple_imgs(illusts_json: 'Json') -> None:
    HASHTAG = f'{c.RED}#'
    HAS = f'{c.RESET} has {c.BLUE}'
    OF_PAGES = f'{c.RESET} pages'
    _ = [print(f'{HASHTAG}{index}{HAS}{number}{OF_PAGES}', end=', ')
         for (index, _json) in enumerate(illusts_json)
         if (number := _json['page_count']) > 1]
    print('')


def url_given_size(post_json: 'Json', size: str) -> str:
    """
    size : str
        One of: ("square-medium", "medium", "large")
    """
    return post_json['image_urls'][size]


def post_title(current_page_illusts: 'Json', post_number: int) -> str:
    return current_page_illusts[post_number]['title']


def medium_urls(current_page_illusts: 'Json') -> 'list[str]':
    return flow(
        current_page_illusts,
        Map(url_given_size(_, size='square_medium')),
    )


def post_titles_in_page(current_page_illusts: 'Json') -> 'list[str]':
    return flow(
        current_page_illusts,
        len,
        range,
        Map(lambda num: post_title(current_page_illusts, num)),
    )


def page_urls_in_post(post_json: 'Json', size='medium') -> 'list[str]':
    """Get the number of pages and each of their urls in a multi-image post."""
    number_of_pages = post_json['page_count']
    if number_of_pages > 1:
        list_of_pages = post_json['meta_pages']
        return [url_given_size(list_of_pages[i], size)
                for i in range(number_of_pages)]
    else:
        return [url_given_size(post_json, size)]


def change_url_to_full(url: str, png=False) -> str:
    """
    The 'large' resolution url isn't the largest. This uses changes the url to
    the highest resolution available
    """
    url = re.sub(r'_master\d+', '', url)
    url = re.sub(r'c\/\d+x\d+_\d+_\w+\/img-master', 'img-original', url)

    # If it doesn't work, try changing to png
    if png:
        url = url.replace('jpg', 'png')
    return url


def process_user_url(url_or_id: str) -> str:
    if 'users' in url_or_id:
        if '\\' in url_or_id:
            user_input = split_backslash_last(url_or_id).split('\\')[-1][1:]
        else:
            user_input = split_backslash_last(url_or_id)
    else:
        user_input = url_or_id
    return user_input


def process_artwork_url(url_or_id: str) -> str:
    if 'artworks' in url_or_id:
        user_input = split_backslash_last(url_or_id).split('\\')[0]
    elif 'illust_id' in url_or_id:
        user_input = re.findall(r'&illust_id.*', url_or_id)[0].split('=')[-1]
    else:
        user_input = url_or_id
    return user_input


def newnames_with_ext(urls, oldnames_with_ext, newnames: 'list[str]') -> 'list[str]':
    return flow(
        urls,
        len,
        range,
        lambda r: map(prefix_filename, oldnames_with_ext, newnames, r),
        list
    )

def full_img_details(url: str, png=False) -> (str, str, Path):
    # Example of an image that needs to be downloaded in png: 77803142
    url = change_url_to_full(url, png=png)
    filename = split_backslash_last(url)
    filepath = generate_filepath(filename)
    return url, filename, filepath


def concat_seqs_to_int(keyseqs: 'list[str]', start: int = 0) -> int:
    """Takes prompt input key seqs, combine two digits literally as int"""
    first = keyseqs[start]
    second = keyseqs[start + 1]
    return int(f'{first}{second}')


# From lscat
def ncols(term_width: int, img_width: int, padding: int) -> int:
    return round(term_width / (img_width + padding))

def nrows(term_height: int, img_height: int, padding: int) -> int:
    return term_height // (img_height + padding)

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

def generate_orders(total_pics: int, artists_count: int) -> 'list[int]':
    """Returns the order of images to be displayed
    images 0-29 are artist profile pics
    images 30-119 are previews, 3 for each artist
    so the valid order is:
    0, 30, 31, 32, 1, 33, 34, 35, 2, 36, 37, 38, ...
    """
    order = [x + artists_count - 1 - floor(x/4) for x in range(total_pics)]
    order[0::4] = range(artists_count)
    return order

