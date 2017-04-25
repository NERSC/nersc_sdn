#!/bin/bash

for service in $@ ; do
  echo "service: $service"
  if  [ $(echo $service|grep -c "munge:") -gt 0 ] ; then
    socket=$(echo $service|awk -F: '{print $2}')
    key=$(echo $service|awk -F: '{print $3}')
    cp /config/$key.key /etc/munge/$socket.key
    chown munge /etc/munge/$socket.key
    chmod 600 /etc/munge/$socket.key
    runuser -u munge -- /usr/sbin/munged  -S /var/run/munge/${socket}.socket --key-file=/etc/munge/$socket.key --force -F &
  elif  [ $(echo $service|grep -c "api") -gt 0 ] ; then
    echo "Starting API service"
    cd /src/
    ./sdnapi.py &
  else
    echo "$service not recognized"
  fi
done

wait

if [ $# -eq 0 ] ; then
  bash
fi
