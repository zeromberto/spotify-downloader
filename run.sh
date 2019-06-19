#!/bin/bash
# Get playlists
python3 spotdl.py -u"${USERNAME}"

# Download playlists
DOWNLOAD_PATH=${DOWNLOAD_PATH:-"/data"}
LOG_LEVEL=${LOG_LEVEL:-"INFO"}
python3 spotdl.py --list="." -f "${DOWNLOAD_PATH}" -ll "${LOG_LEVEL}"

chmod -R 777 ${DOWNLOAD_PATH}/*
