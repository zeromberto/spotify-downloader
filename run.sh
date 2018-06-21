#!/bin/bash

foo=${INTERVAL:="24h"}
while true; do
	python spotdl.py -u"${USERNAME}"
	foo=${POSTFIX:="_d"}
	FILEENDING="*${POSTFIX}.txt"
	for i in ${FILEENDING}; do
    	[ -f "$i" ] || break
		folder=${i%_*}
		mkdir -p "/down/$folder"
		python spotdl.py --list="$i" -f "/down/$folder"
	done
	chmod -R 777 /down/*
	sleep "${INTERVAL}"
done
