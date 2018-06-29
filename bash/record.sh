#!/usr/bin/env bash

pactl load-module module-null-sink sink_name=steam
pactl move-sink-input 1 steam
parec -d steam.monitor | oggenc -b 192 -o "$1".ogg --raw -