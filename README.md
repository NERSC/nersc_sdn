# NERSC SDN API service

This service provides a simple REST interface that can be used to instantiate and remove routing rules on a VyOS based router.

## REST API

### Associate
HEADER: “authentication: \<munge\>” \
POST /associate/ \
DATA (JSON Encoded)

```javacript
{
  "end_time": <int: end time in epoch form>,
  “jobid": "<string: SLURM JOB ID>",
  "user": "<string: user name>"
}
```

RETURNS: JSON encoded hash with address.

```javascript
{
  "address": "128.55.224.13"
}
```

### Associate for a specific node
HEADER: “authentication: \<munge\>” \
POST /associate/\<ip\> \
DATA (JSON Encoded)

```javascript
{
  "end_time": <int: end time in epoch form>,
  “jobid": "<string: SLURM JOB ID>",
  "user": "<string: user name>"
}
```

Note: IP is the internal IP address to be mapped.

RETURNS: JSON encoded hash with address.

```javascript
{
  "address": "128.55.224.13"
}
```

## Configuration

Configuration is controlled by the nersc_sdn.conf file.  It supports the
following settings.

* DBHOST: hostname of the mongo host.
* RTRUSER: Username to use for the ssh connection to the router.
* MAPFILE: Path to the map file.
* AUTHMODE: Authentication mode.  Only munge is supported.
* ALLOWED: List of users by uid that are allowed to make requests.
* JOBSURL: URL of the job server.
* POLLINTERVAL: Frequency to check for completed jobs.

Dynamic DNS

In addition the following settings are aviable to configure dynamic DNS
* DNS_BASE: Base part of the name
* DNS_ZONE: Parameter for the zone transfer
* DNS_SERVER: Server to use for the name request
* DNS_KEYFILE: Path to the keyfile for the request
* DNS_PREFIX: Prefix for the name.

The name assoicated with the IP during a job has the format of [_prefix_]*[Job Number]*.[_base_].  For example if DNS_BASE is 'gerty.services.nersc.gov' and DNS_PREFIX is 'job' for job 123, then name would be 'job123.gerty.services.nersc.gov'.


## Testing setUp

To run a test instance of the server do the following.

    ./test/genconfig.sh
    docker-compose up -d

If you haven't done so before, you will need to initialize the database.

    docker-compose exec api bash
    # /src/sdninitdb.py mongo 10.10.10 1:5
    # exit


To build the test image do a docker build against Dockerfile.test.

    docker build -t sdntest -f Dockerfile.test .

To test things, ssh to the node container and run cli.py commands.

    ssh -o stricthostkeychecking=no -i ./tconfig/ssh -p 2230  root@localhost
    cli.py
    SLURM_JOBID=1234 cli.py associate
    cli.py
    cli.py release
    cli.py
