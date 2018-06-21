#!/bin/bash

echo "1 2" | python spotdl.py -uze.romberto
for i in *_d.txt; do
    [ -f "$i" ] || break
	folder=${i%_*}
	mkdir -p "/down/$folder"
	python spotdl.py --list="$i" -f "/down/$folder"
done
chmod -R 777 /down/*
