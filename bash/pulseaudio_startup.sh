#!/usr/bin/env bash

pulseaudio --log-level=4 --log-target=stderr -v
pacmd load-module module-virtual-sink sink_name=v1
pacmd set-default-sink v1
# set the monitor of v1 sink to be the default source
pacmd set-default-source v1.monitor

pacmd load-module module-loopback sink=v1
