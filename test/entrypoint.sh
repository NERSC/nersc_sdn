#!/bin/bash

#
# Check for config
#
if [ ! -e /config ] ; then
  echo "Missing config directory."
  echo "Use the volume mount to pass in configuration data."
  exit 1
fi

# Add the key, entrypoint and munge key
if [ -e /config/ssh.pub ] ; then
  chmod 700 /root/.ssh
  chown -R root /root/.ssh
  cp /config/ssh.pub /root/.ssh/authorized_keys
fi

# Copy and fix up munge key
#
if [ -e /config/munge.key ] ; then
  cp /config/munge.key /etc/munge/munge.key
  chmod 600 /etc/munge/munge.key
  chown munge /etc/munge/munge.key && \
  chown munge /etc/munge/munge.key
fi

#
# Add a test user if ADDUSER is defined
#
if [ ! -z "$ADDUSER" ] ; then
  useradd -m $ADDUSER -s /bin/bash
  cp -a /root/.ssh/ /home/$ADDUSER/
  chown $ADDUSER -R /home/$ADDUSER/.ssh/
fi

#
# mapfile
if [ -e /config/mapfile ] ; then
  mkdir /etc/nersc_sdn
  cp /config/mapfile  /etc/nersc_sdn/mapfile
fi

for service in $@ ; do
  echo "service: $service"
  if  [ $(echo $service|grep -c "munge") -gt 0 ] ; then
    /etc/init.d/munge start
  elif  [ $(echo $service|grep -c "api") -gt 0 ] ; then
    echo "Starting API service"
    cd /src/
    gunicorn -b 0.0.0.0:5000 nersc_sdn.sdnapi:application &
  elif  [ $(echo $service|grep -c "ssh") -gt 0 ] ; then
    /usr/sbin/sshd -D
  else
    echo "$service not recognized"
  fi
done

wait

if [ $# -eq 0 ] ; then
  bash
fi
