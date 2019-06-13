#!/bin/bash
# Get playlists
python3 spotdl.py -u"${USERNAME}"
FILEENDING="*${POSTFIX:-"_d"}.txt"
PATH_PREFIX=${PATH_PREFIX:-"/data"}

# Download tracks within playlists with postfix
for i in ${FILEENDING}; do
    [[ -f "$i" ]] || break
    folder=${i%_*}
    mkdir -p "${PATH_PREFIX}/$folder"
    python3 spotdl.py --list="$i" -f "${PATH_PREFIX}/$folder" -ll DEBUG

    if [[ -f "$i" ]]; then
        rm "$i"
    fi
done
chmod -R 777 ${PATH_PREFIX}/*
