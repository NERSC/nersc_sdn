
from __future__ import print_function
from pymongo import MongoClient
import time
from nersc_sdn import vyos_interface
from nersc_sdn.ddns import DDNS
import logging
import requests
import json
from subprocess import Popen, PIPE, STDOUT
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
        key = None
        if 'RTRKEY' in settings:
            key = settings['RTRKEY']
        self.map = self._load_mapfile(mapfile)
        self.vyos = vyos_interface.vyosInterface(user, key=key)
        self.ddns = self._init_dns(settings)
        self.shutdown_file = settings.get('SHUTFILE', "/tmp/shutdown_sdn")
        self.collection = settings.get('COLLECTION', 'routes')
        self.cleanup_proc = Process(target=self.cleanup,
                                    name='CleanupThread')
        self.cleanup_proc.start()
        client = MongoClient(self.dbhost)
        self.routes = client.sdn[self.collection]
        if self.routes.find_one() is None:
            self.cleanup_proc.terminate()
            raise OSError('DB not initialized')

    def _init_dns(self, settings):
        has_ddns_param = False
        dnsparams = ['DNS_BASE', 'DNS_ZONE', 'DNS_SERVER', 'DNS_KEYFILE',
                     'DNS_PREFIX']
        for p in dnsparams:
            if p in settings:
                has_ddns_param = True
        if has_ddns_param:
            # Now make sure all are provided
            for param in dnsparams:
                if param not in settings:
                    raise ValueError("Missing %s parameter" % (param))
            return DDNS(base=settings['DNS_BASE'],
                        prefix=settings['DNS_PREFIX'],
                        keyfile=settings['DNS_KEYFILE'],
                        server=settings['DNS_SERVER'],
                        zone=settings['DNS_ZONE'])
        return None

    def shutdown(self):
        self.cleanup_proc.terminate()

    def cleanup(self):
        client = MongoClient(self.dbhost)
        self.routes = client.sdn[self.collection]
        if self.routes.find_one() is None:
            print("DB not intialized")
            return -1
        while True:
            if os.path.exists(self.shutdown_file):
                print("Shut down triggered")
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

    def _get_slurm(self):
        p = Popen('squeue -h -t R -o %%A', shell=True,
                  stdout=PIPE,
                  stderr=STDOUT)
        jobs = []
        for line in p.stdout.readlines():
            jobs.append(line.rstrip())
        return jobs

    def get_jobs(self):
        if self.agent == 'local':
            jobs = self._get_slurm()
        else:
            r = requests.get(self.agent)
            jobs = json.loads(r.text)
        return jobs

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
        required = ['uid', 'end_time', 'jobid']
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
        if 'user' not in data:
            data['user'] = 'unknown'
        update = {
            'status': ASSIGNING,
            'ip': ip,
            'router': router,
            'end_time': data['end_time'],
            'user': data['user'],
            'uid': data['uid'],
            'jobid': str(data['jobid']),
            'last_associated': time.time()
        }
        self.routes.update({'address': address}, {'$set': update})
        self.vyos.add_nat(ip, router, address)
        update = {
            'status': USED,
            'last_associated': time.time()
        }
        self.routes.update({'address': address}, {'$set': update})
        if self.ddns is not None:
            self.ddns.add_dns(str(data['jobid']), address)
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
            'router': None,
            'end_time': None,
            'jobid': None,
            'user': None,
            'uid': None
        }
        self.routes.update({'ip': ip}, {'$set': update})
        if self.ddns is not None:
            self.ddns.del_dns(rec['jobid'])
        return "released"
