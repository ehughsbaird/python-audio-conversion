# python-convert-m4a-to-mp3

Since my car's entertainment system only supports `.mp3` files for audio,
and a decent portion of my music collection is `.m4a` files, I created this
repo for batch converting audio files.

For DRM-protected `.m4p` files that I purchased through iTunes, I created playlists
of them, burned those to CDs, and then re-imported them as `.m4a` files.

Converting a `.m4a` file to a `.mp3` file can be done easily with `ffmpeg`
(e.g. `ffmpeg -i "$m4a_file" -codec:a libmp3lame -qscale:a 1 "$mp3_file"`),
but this does not transfer the metadata (artist, album, song, etc.).
See the `bash-convert-m4a-to-mp3-NO-METADATA.sh` file in this repo for an example.


### Create working copy of the music files

As I would prefer not to create extraneous copies in my main music collection,
I copied all of the `.mp3` and `.m4a` files to a separate directory for processing:

```
SOURCE_DIR="$HOME/Music/iTunes/iTunes Media/Music"
TARGET_DIR="$HOME/Music/tmp/convert-m4a-to-mp3"
mkdir -p $TARGET_DIR
rsync -av \
  --include '*/' \
  --include '*.mp3' \
  --include '*.m4a' \
  --exclude '*' \
  "$SOURCE_DIR/" \
  "$TARGET_DIR"
```

### Setup

**Install dependencies:**

Note: On my Mac, I've installed `python3` with [Homebrew](https://brew.sh/) and it is located
earlier in `$PATH` than the system version. This means I do not have to use `sudo` or a
[python virtual environment](https://docs.python.org/3/tutorial/venv.html) to install packages.

```
python3 -m pip install pydub mutagen
```


### Run

```
python3 python-convert-m4a-to-mp3.py path/to/directory/to/convert path/to/logfile.log
```
Depending on the size of your music collection this could take quite some time,
so after it is completed, you can check for errors (adjust log file if updated above):
```
grep -A1 -B1 'PROBLEM WITH CONVERTING' /path/to/logfile.log
```
