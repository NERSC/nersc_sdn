# NERSC SDN API service

This service provides a simple REST interface that can be used to instantiate and remove routing rules on a VyOS based router.

## REST API

### Associate
HEADER: “authentication: <munge>”
POST /associate/
DATA (JSON Encoded)
```{
  "end_time": <int: end time in epoch form>,
  “jobid": "<string: SLURM JOB ID>",
  "user": "<string: user name>"
}```

RETURNS: JSON encoded hash with address.
```javascript
{
  "address": "128.55.224.13"
}```

### Associate for a specific node
HEADER: “authentication: <munge>”
POST /associate/<ip>
DATA (JSON Encoded)
```{
  "end_time": <int: end time in epoch form>,
  “jobid": "<string: SLURM JOB ID>",
  "user": "<string: user name>"
}```

Note: IP is the internal IP address to be mapped.

RETURNS: JSON encoded hash with address.
```javascript
{
  "address": "128.55.224.13"
}```

## Testing setUp

To run a test instance of the server do the following.

    ./test/genconfig.sh
    docker-compose up -d

To build the test image do a docker build against Dockerfile.test.

    docker build -t sdntest -f Dockerfile.test .