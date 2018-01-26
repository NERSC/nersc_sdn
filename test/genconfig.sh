#!/bin/sh
CD=`pwd`/tconfig

[ -e $CD ] || mkdir $CD

if [ ! -e $CD/munge.key ] ; then
  dd if=/dev/zero of=$CD/munge.key count=1
fi

if [ ! -e $CD/ssh ] ; then
   ssh-keygen -f $CD/ssh -N ''
fi
if [ ! -e $CD/mapfile ] ; then
  for i in $(seq 100) ; do
    echo "172.17.0.$i:router" >> $CD/mapfile
  done
fi

if [ ! -e $CD/settings.ini ] ; then
   cat << EOF > $CD/settings.ini
DBHOST='mongo'
RTRUSER='sdn'
MAPFILE='/config/mapfile'
POLLINTERVAL=1
EOF

fi

