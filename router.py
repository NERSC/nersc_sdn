
from pymongo import MongoClient
import time
import vyos_interface
import logging

USED = "used"
AVAILABLE = "available"
ASSIGNING = "assigning"
RELEASING = "releasing"


class Router:
    def __init__(self, settings):
        logging.debug("Initializing Router")
        dbhost = settings['DBHOST']
        user = settings['RTRUSER']
        mapfile = settings['MAPFILE']
        self.map = self._load_mapfile(mapfile)
        client = MongoClient(dbhost)
        if client is None:
            raise OSError('Failed to connect to Mongo')
        self.routes = client.sdn.routes
        if self.routes.find_one() is None:
            raise OSError('DB not initialized')
        self.vyos = vyos_interface.vyosInterface(user)

    def _load_mapfile(self, mapfile):
        map = dict()
        with open(mapfile) as f:
            for line in f:
                (ip, router) = line.rstrip().split(':')
                map[ip] = router
        return map

    def _get_router(self, ip):
        # Compute the appropriate router for the ip
        # Probably replace with a mongo table
        if ip not in self.map:
            raise ValueError('Bad IP')
        return self.map[ip]

    def available(self):
        addresses = []
        for rec in self.routes.find({'status': AVAILABLE}):
            addresses.append(rec['address'])
        return addresses

    def status(self):
        resp = []
        for rec in self.routes.find({}):
            rec.pop('_id')
            resp.append(rec)
        return resp

    def check_data(self, data):
        required = ['user', 'end_time', 'jobid']
        for f in required:
            if f not in data:
                raise ValueError('Missing %s' % (f))

    def associate(self, session, data):
        # allocate an address and assocaite it with ip
        ip = session['ip']
        router = self._get_router(ip)
        self.check_data(data)
        if router is None:
            raise ValueError('Invalid IP')
        rec = self.routes.find_one({'ip': ip})
        if rec is not None:
            logging.warn("Already mapped")
            return rec['address']
        rec = self.routes.find_one({'status': AVAILABLE})
        if rec is None:
            logging.warn("No available addresses found")
            return None
        address = rec['address']
        update = {
            'status': ASSIGNING,
            'ip': ip,
            'router': router,
            'end_time': data['end_time'],
            'user': data['user'],
            'jobid': data['jobid'],
            'last_associated': time.time()
        }
        self.routes.update({'address': address}, {'$set': update})
        self.vyos.add_nat(ip, router, address)
        update = {
            'status': USED,
            'last_associated': time.time()
        }
        self.routes.update({'address': address}, {'$set': update})
        return address

    def release(self, ip):
        # release ip
        rec = self.routes.find_one({'ip': ip})
        if rec is None:
            return 'released'
        update = {
            'status': RELEASING,
        }
        self.routes.update({'ip': ip}, {'$set': update})
        self.vyos.remove_nat(rec['router'], rec['address'])
        update = {
            'status': AVAILABLE,
            'ip': None,
            'router': None
        }
        self.routes.update({'ip': ip}, {'$set': update})
        return "released"
