"""Browse pixiv in the terminal using kitty's icat to display images (in the
terminal!)

Usage:
  koneko       [<link> | <searchstr>]
  koneko [1|a] <link_or_id>
  koneko [2|i] <link_or_id>
  koneko (3|f) <link_or_id>
  koneko [4|s] <searchstr>
  koneko [5|n]
  koneko (-h | --help)
  koneko (-v | --version)

Notes:
*  If you supply a link and want to go to mode 3, you must give the (3|f) argument,
   otherwise your link would default to mode 1.
*  It is assumed you won't need to search for an artist named '5' or 'n' from the
   command line, because it would go to mode 5.

Optional arguments (for specifying a mode):
  1 a  Mode 1 (Artist gallery)
  2 i  Mode 2 (Image view)
  3 f  Mode 3 (Following artists)
  4 s  Mode 4 (Search for artists)
  5 n  Mode 5 (Newest works from following artists ("illust follow"))

Required arguments if a mode is specified:
  <link>        Pixiv url, auto detect mode. Only works for modes 1, 2, and 4
  <link_or_id>  Either pixiv url or artist ID or image ID
  <searchstr>   String to search for artists

Options:
  (-h | --help)     Show this help
  (-v | --version)  Show version number
"""

import sys

from docopt import docopt

from koneko import pure, __version__


def process_cli_args():
    """Use docopt to process cli args, returning:
    prompted: bool
        if user needs to be asked for the mode
    main_command: string, 1-5
        if user has specified a mode number
    user_input: string
        if user has entered further information required for the mode
        eg, modes 1/5 requires artist user id; mode 2, requires image id
    """
    args = docopt(__doc__)

    # Handle version or help
    if args['--version'] or args['-v']:
        print(__version__)
        return None, 'vh', None
    elif args['--help'] or args['-h']:
        print(__doc__)
        return None, 'vh', None

    # no cli arguments
    if len(sys.argv) <= 1:
        return True, None, None

    # Yes it's a lie
    print('Logging in...')

    # Argument given, no mode specified
    if url_or_str := args['<link>']:
        if 'users' in url_or_str:
            return False, '1', pure.process_user_url(url_or_str)

        elif 'artworks' in url_or_str or 'illust_id' in url_or_str:
            return False, '2', pure.process_artwork_url(url_or_str)

        # Assume you won't search for '3' or 'f'
        elif url_or_str == '3' or url_or_str == 'f':
            return False, '3', None

        # Assume you won't search for '5' or 'n'
        elif url_or_str == '5' or url_or_str == 'n':
            return False, '5', None

        else:  # Mode 4, string to search for artists
            return False, '4', url_or_str

    # Mode specified, argument can be link or id
    elif url_or_id := args['<link_or_id>']:
        if args['1'] or args['a']:
            return False, '1', pure.process_user_url(url_or_id)

        elif args['2'] or args['i']:
            return False, '2', pure.process_artwork_url(url_or_id)

        elif args['3'] or args['f']:
            return False, '3', pure.process_user_url(url_or_id)

    elif user_input := args['<searchstr>']:
        return False, '4', user_input

    raise Exception("Unknown command line argument!")
