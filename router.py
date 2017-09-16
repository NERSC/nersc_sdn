
from pymongo import MongoClient
import time
import vyos_interface
import logging
import requests
import json
from multiprocessing.process import Process
import os

USED = "used"
AVAILABLE = "available"
ASSIGNING = "assigning"
RELEASING = "releasing"


class Router:
    def __init__(self, settings):
        logging.debug("Initializing Router")
        self.dbhost = settings['DBHOST']
        self.poll = float(settings['POLLINTERVAL'])
        self.agent = settings['JOBSURL']
        user = settings['RTRUSER']
        mapfile = settings['MAPFILE']
        self.map = self._load_mapfile(mapfile)
        self.vyos = vyos_interface.vyosInterface(user)
        self.cleanup_proc = Process(target=self.cleanup,
                                    name='CleanupThread')
        self.cleanup_proc.start()
        client = MongoClient(self.dbhost)
        if client is None:
            self.cleanup_proc.terminate()
            raise OSError('Failed to connect to Mongo')
        self.routes = client.sdn.routes
        if self.routes.find_one() is None:
            self.cleanup_proc.terminate()
            raise OSError('DB not initialized')

    def shutdown(self):
        self.cleanup_proc.terminate()

    def cleanup(self):
        client = MongoClient(self.dbhost)
        if client is None:
            raise OSError('Failed to connect to Mongo')
        self.routes = client.sdn.routes
        while True:
            if os.path.exists("/tmp/shutdown_sdn"):
                print "Shut down triggered"
                return 0
            # Look for expired jobs
            now = time.time()
            for route in self.routes.find({'end_time': {'$lt': now},
                                           'status': 'used'}):
                ip = route['ip']
                logging.warn("route expired %s" % (ip))
                self.release(ip)
            # Get jobs, ignore failures
            try:
                running = self.get_jobs()
                self.check_jobs(running)
            except:
                pass

            time.sleep(self.poll)

    def check_jobs(self, running):
        for route in self.routes.find({'status': 'used'}):
            # check job
            if 'jobid' not in route:
                continue
            if route['jobid'] not in running:
                jobid = route['jobid']
                logging.warn("Job no longer running %s" % (jobid))
                self.release(route['ip'])

    def get_jobs(self):
        r = requests.get(self.agent)
        return json.loads(r.text)

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
