# Convert .wma files to .mp3 files
import argparse
import os
import logging
import sys
import glob
import mutagen
from pydub import AudioSegment
from pathlib import Path

parser = argparse.ArgumentParser(prog='wma to mp3')
parser.add_argument('directory')
parser.add_argument('log_file')

args = parser.parse_args()

# Logging
# Because I want a full log file to potentially reference, but still want to see activity...
# use multiple logging handlers and use ANSI escape code to clear stdout to show a single line
# See https://en.wikipedia.org/wiki/ANSI_escape_code
# If the logging output is longer then the terminal width, it won't be as clean :(

my_logger = logging.getLogger()
my_logger.setLevel(logging.DEBUG) # Switch from 'INFO' to 'DEBUG' for more detailed output

# Handler for logging to file
file_handler = logging.FileHandler(args.log_file, encoding="utf-8")
file_formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
file_handler.setFormatter(file_formatter)

# Handler for showing only a single log line in stdout
stdout_handler_temporary = logging.StreamHandler(sys.stdout)
# ANSI escape codes:
# '\x1b[nD' cursor back 'n' spaces
# '\x1b[K' clear from cursor to end of the line
stdout_formatter_temporary = logging.Formatter('\x1b[200D\x1b[K%(levelname)s: %(message)s')
stdout_handler_temporary.setFormatter(stdout_formatter_temporary)
stdout_handler_temporary.terminator = '\r' # Should also set the cursor to the beginning of the line

# Handler for typical display of stdout lines
stdout_handler_permanent = logging.StreamHandler(sys.stdout)
stdout_formatter_permanent = logging.Formatter('%(levelname)s: %(message)s')
stdout_handler_permanent.setFormatter(stdout_formatter_permanent)

def switch_stdout_logger(temp_or_perm):
    # Need to clear old handlers
    for handler in my_logger.handlers[:]:
        my_logger.removeHandler(handler)
    # re-add appropriate loggers
    my_logger.addHandler(file_handler)
    if temp_or_perm == 'temp':
        my_logger.addHandler(stdout_handler_temporary)
    elif temp_or_perm == 'perm':
        my_logger.addHandler(stdout_handler_permanent)

# Show the first message and then switch to showing only a single line
switch_stdout_logger('perm')
my_logger.info('Starting conversion scan of: %s' % args.directory)
switch_stdout_logger('temp')

def short_file_name(file_name):
    return file_name.lstrip(args.directory)


# WMA tags and mp3 tags have different names.
# Here's a handy lookup of the ones we care about
mappable = {
        'Author': 'artist',
        'Title': 'title',
        'WM/AlbumArtist': 'albumartist',
        'WM/AlbumTitle': 'album',
        'WM/Composer': 'composer',
        'WM/Genre': 'genre',
        'WM/TrackNumber': 'tracknumber',
        'WM/Year': 'date'
}

def convert_to_mp3(wma_file):
    my_logger.debug(r'wma file: %s', short_file_name(wma_file))
    mp3_file = wma_file[:-4] + '.mp3'
    if os.path.exists(mp3_file):
        my_logger.info(r'mp3 file already exists: %s', short_file_name(mp3_file))
    else:
        try:
            # Create mp3 file
            my_logger.info(r'Creating mp3 file: %s' % short_file_name(mp3_file))
            AudioSegment.from_file(wma_file).export(mp3_file, format='mp3')

            # Copy appropiate tags from wma file to mp3 file
            my_logger.debug(r'Reading file tags: %s' % short_file_name(wma_file))
            wma_tags = mutagen.File(wma_file, easy=True)
            mp3_tags = mutagen.File(mp3_file, easy=True)
            for tag in mappable.keys():
                if tag in wma_tags:
                    my_logger.debug('writing tag %s: %s' % (mappable[tag], wma_tags[tag]))
                    if(tag == 'WM/Year'):
                        for val in wma_tags[tag]:
                            mp3_tags[mappable[tag]] = str(val)
                    else:
                        mp3_tags[mappable[tag]] = wma_tags[tag]
            mp3_tags.save()
            print(f"{mp3_file}: {mp3_tags}")
        except Exception:
            my_logger.exception('PROBLEM WITH CONVERTING: %s' % (short_file_name(wma_file)))
            return


# Iterate through .wma files in 'args.directory'
for root, dirs, files in os.walk(args.directory):
    for file in files:
        filename = os.path.join(root, file)
        if not filename.endswith('.wma'):
            continue
        convert_to_mp3(filename)

# Reset stdout formatter to show the final message
switch_stdout_logger('perm')
my_logger.info('Finished conversion scan of: %s' % args.directory)
