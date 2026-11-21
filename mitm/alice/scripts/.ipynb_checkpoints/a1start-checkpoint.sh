#!/bin/bash

echo "Starting up a1start.sh" >> /tmp/a2.log

HOST="alice-lan0"
URL="cgi-bin/access1.cgi?line="
SLEEP=10
LOOP=0

function grab_loop {
	echo $LOOP

	NUM=$(($NUM + 1))
	curl http://$HOST/$URL$NUM | grep -v "XXX END OF LINE XXX" >> /tmp/a1.log
}


while true; do
	NUM=$(($RANDOM % 4500))
	echo "================== STARTING TRANSFER ====================="
	LOOP=$(( $LOOP + 1 ))
	while grab_loop; do
		sleep $(($RANDOM % $SLEEP))
	done
done

