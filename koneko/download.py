import os
import itertools
from pathlib import Path
from functools import partial
from concurrent.futures import ThreadPoolExecutor

from pipey import Pipeable as P

from koneko import api, pure, utils


def newnames_with_ext(urls, oldnames_with_ext, newnames: 'list[str]') -> 'list[str]':
    return (
        urls
        >> P(len)
        >> P(range)
        >> P(lambda r: map(pure.prefix_filename, oldnames_with_ext, newnames, r))
        >> P(list)
    )

def async_download_core_rename(download_path, urls, newnames, tracker=None):
    oldnames_ext = urls >> pure.Map(pure.split_backslash_last)
    newnames_ext = newnames_with_ext(urls, oldnames_ext, newnames)
    async_download_core(download_path, urls, oldnames_ext, newnames_ext,
                        tracker)

def async_download_core_no_rename(download_path, urls, tracker=None):
    oldnames_ext = urls >> pure.Map(pure.split_backslash_last)
    async_download_core(download_path, urls, oldnames_ext, oldnames_ext,
                        tracker)

def async_download_core(download_path, urls, oldnames_with_ext, newnames_with_ext,
                        tracker=None):
    """
    Rename files with given new name if needed.
    Submit each url to the ThreadPoolExecutor, so download and rename are concurrent
    """
    # Nothing needs to be downloaded
    if not urls:
        return True

    # Filter out already downloaded files
    downloaded_newnames = itertools.filterfalse(os.path.isfile, newnames_with_ext)
    downloaded_oldnames = itertools.filterfalse(os.path.isfile, oldnames_with_ext)
    helper = partial(downloadr, tracker=tracker)

    os.makedirs(download_path, exist_ok=True)
    with utils.cd(download_path):
        with ThreadPoolExecutor(max_workers=len(urls)) as executor:
            executor.map(helper, urls, downloaded_oldnames, downloaded_newnames)


def downloadr(url, img_name, new_file_name=None, tracker=None):
    """Actually downloads one pic given one url, rename if needed."""
    api.myapi.protected_download(url)

    if new_file_name:
        # This character break renames
        if '/' in new_file_name:
            new_file_name = new_file_name.replace('/', '')
        os.rename(img_name, new_file_name)
        img_name = new_file_name

    if tracker:
        tracker.update(img_name)


# - Wrappers around above download functions, for downloading multi-images
def download_page(data, tracker=None):
    """
    Download the illustrations on one page of given artist id (using threads),
    rename them based on the *post title*. Used for gallery modes (1 and 5)
    """
    urls = pure.medium_urls(data.current_illusts)
    titles = pure.post_titles_in_page(data.current_illusts)

    async_download_core_rename(
        data.download_path, urls, newnames=titles,
        tracker=tracker
    )

def user_download(data, tracker=None):
    async_download_core_rename(
        data.download_path,
        data.all_urls,
        newnames=data.all_names,
        tracker=tracker
    )

def init_download(data, download_func, tracker):
    if utils.dir_not_empty(data):
        return True

    if data.page_num == 1:
        print('Cache is outdated, reloading...')
    if data.download_path.is_dir():
        os.system(f'rm -r {data.download_path}')  # shutil.rmtree is better

    download_func(data, tracker=tracker)

    # Save the number of artists == splitpoint
    # So later accesses, which will not request, can display properly
    if download_func == user_download:
        with utils.cd(data.download_path):
            with open('.koneko', 'w') as f:
                f.write(str(data.splitpoint))

    return True

# - Wrappers around the core functions for downloading one image
@utils.spinner('')
def async_download_spinner(download_path, urls):
    """Batch download and rename, with spinner. For mode 2; multi-image posts"""
    async_download_core_no_rename(
        download_path,
        urls,
        newnames=None,
    )

@utils.spinner('')
def download_core(large_dir, url, filename, try_make_dir=True):
    """Downloads one url, intended for single images only"""
    if try_make_dir:
        os.makedirs(large_dir, exist_ok=True)
    if not Path(filename).is_file():
        print('   Downloading illustration...', flush=True, end='\r')
        with utils.cd(large_dir):
            downloadr(url, filename)


def full_img_details(url, png=False):
    # Example of an image that needs to be downloaded in png: 77803142
    url = pure.change_url_to_full(url, png=png)
    filename = pure.split_backslash_last(url)
    filepath = pure.generate_filepath(filename)
    return url, filename, filepath

def download_url_verified(url, png=False):
    # Returned url might be different if png is True
    url, filename, filepath = full_img_details(url, png=png)
    download_path = Path('~/Downloads').expanduser()

    download_core(download_path, url, filename, try_make_dir=False)

    verified = utils.verify_full_download(filepath)
    if not verified:
        download_url_verified(url, png=True)
    else:
        print(f'Image downloaded at {filepath}\n')

# Download full res from ui, on user demand
def download_image_coords(data, first_num, second_num):
    selected_image_num = utils.find_number_map(int(first_num), int(second_num))
    # 0 is acceptable, but is falsy; but 0 'is not' False
    if selected_image_num is False:
        print('Invalid number!')
    else:
        download_image_num(data, selected_image_num)

def download_image_num(data, number):
    # Update current_page_illusts, in case if you're in another page
    download_url_verified(data.url(number))
