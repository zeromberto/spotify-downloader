#!/bin/bash
# Get playlists
python3 spotdl.py -u"${USERNAME}"

# Download playlists
DOWNLOAD_PATH=${DOWNLOAD_PATH:-"/data"}
python3 spotdl.py --list="." -f "${DOWNLOAD_PATH}"

chmod -R 777 ${DOWNLOAD_PATH}/*
