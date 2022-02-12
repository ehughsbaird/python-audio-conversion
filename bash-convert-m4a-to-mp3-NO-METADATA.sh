#!/bin/bash
# Convert .m4a to .mp3 files
# DOES NOT INCLUDE ID3 METADATA IN CREATED .mp3 FILES!!!

MUSIC_DIR="/Volumes/KINGSTON/Music"  ### Edit to match desired path
LOGFILE="$HOME/music_convert.log"

if ! `which ffmpeg 2>&1 >/dev/null`; then
  EXIT_CODE=$?
  echo "ERROR: 'which ffmpeg' returns a non-zero exit code: $EXIT_CODE"
  echo "ERROR: Is 'ffmpeg' installed and in the \$PATH?"
  exit $EXIT_CODE
fi

echo "NOTE: Appending logs to: $LOGFILE"
echo "`date` STARTING CONVERSION OF '$MUSIC_DIR'" | tee -a $LOGFILE

find "$MUSIC_DIR" -type f | sort | grep \.m4a$ > /tmp/m4a_music_files

while IFS= read -r line; do
  m4a_file="$line"
  mp3_file="`echo $m4a_file | sed 's#\.m4a$#.mp3#'`"
  if [ -f "$mp3_file" ]; then
    echo "ALREADY EXISTS: $mp3_file"
  else
    echo "CONVERTING: $m4a_file" | tee -a $LOGILE
    if ! $(ffmpeg -i "$m4a_file" -codec:a libmp3lame -qscale:a 1 "$mp3_file"); then
      echo "FAILED:     $mp3_file" | tee -a $LOGFILE
    else
      echo "CREATED:    $mp3_file" | tee -a $LOGFILE
    fi
  fi
done < /tmp/m4a_music_files

echo "`date` ENDING CONVERSION OF '$MUSIC_DIR'" | tee -a $LOGFILE
