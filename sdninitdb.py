#!/usr/bin/python

from pymongo import MongoClient
import sys


def init(db, base, imin, imax):
    client = MongoClient(db)
    routes = client["sdn"].routes

    routes.remove({})
    for ip in range(imin, imax+1):
        address = '%s.%d' % (base, ip)
        rec = {
            'address': address,
            'ip': None,
            'router': None,
            'last_associated': None,
            'end_time': None,
            'user': None,
            'jobid': None,
            'status': 'available'
        }
        routes.insert(rec)


if __name__ == '__main__':
    irange = sys.argv[3].split(':')
    imin = int(irange[0])
    imax = int(irange[1])
    init(sys.argv[1], sys.argv[2], imin, imax)
