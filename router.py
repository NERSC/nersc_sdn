
from pymongo import MongoClient
import time
import vyos_interface

USED = "used"
AVAILABLE = "available"
ASSIGNING = "assigning"
RELEASING = "releasing"


class Router:
    def __init__(self):
        print "Initializing Database"
        client = MongoClient("localhost")
        if client is None:
            raise OSError('Failed to connect to Mongo')
        self.routes = client.sdn.routes
        if self.routes.find_one() is None:
            raise OSError('DB not initialized')
        self.vyos = vyos_interface.vyosInterface()

    def get_router(self, nid):
        # Compute the appropriate router for the nid
        # Probably replace with a mongo table
        return "cori.nersc.gov"

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

    def associate(self, nid):
        # allocate an address and assocaite it with nid
        rec = self.routes.find_one({'nid': nid})
        if rec is not None:
            print "Already mapped"
            return rec['address']
        rec = self.routes.find_one({'status': AVAILABLE})
        if rec is None:
            print "No available addresses found"
            return None
        address = rec['address']
        router = self.get_router(nid)
        update = {
            'status': ASSIGNING,
            'nid': nid,
            'router': router,
            'last_associated': time.time()
        }
        self.routes.update({'address': address}, {'$set': update})
        self.vyos.add_nat(nid, router, address)
        update = {
            'status': USED,
            'last_associated': time.time()
        }
        self.routes.update({'address': address}, {'$set': update})
        return address

    def release(self, nid):
        # release nid
        rec = self.routes.find_one({'nid': nid})
        if rec is None:
            return 'released'
        update = {
            'status': RELEASING,
        }
        self.routes.update({'nid': nid}, {'$set': update})
        self.vyos.remove_nat(nid, rec['router'], rec['address'])
        update = {
            'status': AVAILABLE,
            'nid': None,
            'router': None
        }
        self.routes.update({'nid': nid}, {'$set': update})
        return "released"
