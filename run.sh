#!/bin/bash
# Get playlists
python3.6 spotdl.py -u"${USERNAME}"
foo=${POSTFIX:="_d"}
FILEENDING="*${POSTFIX}.txt"

# Download tracks within playlists with postfix
for i in ${FILEENDING}; do
    [ -f "$i" ] || break
    folder=${i%_*}
    mkdir -p "/data/$folder"
    python3.6 spotdl.py --list="$i" -f "/data/$folder"

    if [ -f "$i" ]; then
        rm "$i"
    fi
done
chmod -R 777 /data/*
