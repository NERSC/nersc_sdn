#!/usr/bin/env python
from __future__ import print_function

import requests
import sys
from nersc_sdn.munge import munge
import json
import os
import pwd
from time import time
import subprocess


def read_config():
    cfgfile = "/etc/nersc_sdn.conf"
    if 'SDN_CONF' in os.environ:
        cfgfile = os.environ['SDN_CONF']
    if not os.path.exists(cfgfile):
        return {}
    confs = dict()
    with open(cfgfile) as f:
        for line in f:
            try:
                k, v = line.rstrip().split('=')
                k = k.strip()
                v = v.lstrip().replace("'", '')
                confs[k] = v
            except:
                pass
    return confs


def get_time(jobid):
    cmd = 'squeue -o %%L -j %s -h' % (jobid)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    line = p.stdout.readlines()[0]
    retval = p.wait()
    if type(line) == bytes:
        line = line.decode('ascii')
    etime = line.rstrip().split(':')
    if retval != 0:
        raise RuntimeError("Squeue failed")
    if len(etime) == 2:
        seconds = int(etime[1])*60+int(etime[0])
    elif len(etime) == 3:
        seconds = int(etime[2])*3600+int(etime[1])*60+int(etime[0])
    else:
        print("WARNING: squeue query failed.  Using  86,400")
        seconds = 86400
    return int(seconds+time())


cv = read_config()

url = cv.get('api_url', 'http://localhost:5000')

header = {'authentication': munge('')}

if len(sys.argv) == 1 or sys.argv[1] == 'status':
    try:
        r = requests.get(url+'/status/', headers=header)
        data = json.loads(r.text)
    except:
        print("Error talking to API server")
        sys.exit(1)
    print("Ext IP          Int. IP         Status     Router")
    print("=======================================================")
    for r in data:
        print('%-15s %-15s %-10s %-10s' % (r['address'], r['ip'],
                                           r['status'], r['router']))

elif len(sys.argv) > 1 and sys.argv[1] == 'associate':
    if 'SLURM_JOBID' not in os.environ:
        print("SLURM_JOBID not set.")
        sys.exit(1)
    jobid = os.environ['SLURM_JOBID']
    user = pwd.getpwuid(os.getuid()).pw_name
    try:
        e_time = get_time(jobid)
    except:
        print("Querying SLURM failed")
        sys.exit(1)

    d = {'end_time': e_time,
         'jobid': jobid,
         'user': user}
    try:
        jdata = json.dumps(d)
        r = requests.post(url+'/associate/', headers=header, data=jdata)
        resp = json.loads(r.text)
        print(resp['address'])
    except:
        print("Error talking to API server")
        sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == 'release':
    try:
        r = requests.get(url+'/release/', headers=header)
        resp = json.loads(r.text)
        print(resp['status'])
    except requests.exceptions.ConnectionError:
        print("Error talking to API server")
        sys.exit(1)
    except:
        print("Error retrieving results")
        sys.exit(1)
else:
    print("Invalid command: %s" % (sys.argv[1]))
    print("Usage: %s <status|associate|release>" % (sys.argv[0]))
