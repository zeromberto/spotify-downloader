#!/usr/bin/env bash
pacmd load-module module-virtual-sink sink_name=v1
pacmd set-default-sink v1

# set the monitor of v1 sink to be the default source
pacmd set-default-source v1.monitor

# Start the ffmpeg capture to an audio file
ffmpeg -f pulse -i default /data/piano.mp3
