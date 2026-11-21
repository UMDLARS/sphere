#!/bin/bash

echo "Starting up a2start.sh" >> /tmp/a2.log

HOST="alice-lan0"
URL="cgi-bin/access2.cgi?line="
SLEEP=10
LOOP=0

function grab_loop {
	echo $LOOP

	NUM=$(($NUM + 1))
	curl --insecure https://$HOST/$URL$NUM | grep -v "XXX END OF LINE XXX" >> /tmp/a2.log
}


while true; do
	NUM=$(($RANDOM % 4000))
	echo "================== STARTING TRANSFER ====================="
	LOOP=$(( $LOOP + 1 ))
	while grab_loop; do
		sleep $(($RANDOM % $SLEEP))
	done
done

