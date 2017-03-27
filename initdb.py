#!/usr/bin/python

from pymongo import MongoClient
import sys

client = MongoClient("localhost")
routes = client["sdn"].routes

base = sys.argv[1]
irange = sys.argv[2].split(':')
imin = int(irange[0])
imax = int(irange[1])
routes.remove({})
for ip in range(imin, imax+1):
    address = '%s.%d' % (base, ip)
    print "Adding %s" % (address)
    rec = {
        'address': address,
        'nid': None,
        'router': None,
        'last_associated': None,
        'status': 'available'
    }
    routes.insert(rec)
    print address
