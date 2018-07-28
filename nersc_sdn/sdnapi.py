#!/usr/bin/python

import pprint
from flask import Flask, jsonify, request
import nersc_sdn.router as router
import auth
import os
import json

application = Flask(__name__)
pp = pprint.PrettyPrinter(indent=4)
application.config['DBHOST'] = 'localhost'
application.config['RTRUSER'] = 'sdn'
application.config['MAPFILE'] = './mapfile'
application.config['AUTHMODE'] = 'munge'
application.config['ALLOWED'] = [0]
application.config['JOBSURL'] = 'http://localhost:8000'

cfgfile = '/etc/nersc_sdn.conf'
if 'SDN_SETTINGS' in os.environ:
    cfgfile = os.environ['SDN_SETTINGS']

if os.path.exists(cfgfile):
    application.logger.info("Loading settings from " +
                            cfgfile)
    application.config.from_pyfile(cfgfile)

application.logger.debug(application.config)

router = router.Router(application.config)

auth_mode = application.config['AUTHMODE']
auth_handler = auth.Authentication({'authentication': auth_mode})
AUTH_HEADER = 'authentication'


def shutdown():
    router.shutdown()


@application.route("/")
def hello():
    return "/{associate,release}"


def is_allowed(session):
    if 'uid' not in session:
        return False
    if session['uid'] in application.config['ALLOWED']:
        return True
    return False


@application.errorhandler(404)
def not_found(error=None):
    """ Standard error function to return a 404. """
    application.logger.warning("404 return")
    message = {
        'status': 404,
        'error': str(error),
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


def unauthorized(error=None):
    message = {
        'status': 401,
        'error': str(error),
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 401
    return resp


@application.route("/_ping")
def ping():
    return ''


@application.route("/v1/associate/", methods=["POST"])
def associate():
    resp = {}
    try:
        rqd = request.get_data()
        data = json.loads(rqd)
    except:
        application.logger.warn("Unable to parse pull data '%s'" % (rqd))
        return not_found()
    try:
        authstr = request.headers.get(AUTH_HEADER)
        session = auth_handler.authenticate(authstr)
        if not is_allowed(session):
            return unauthorized()
        address = router.associate(session, data)
    except:
        return not_found()

    resp['address'] = address
    return jsonify(resp)


@application.route("/v1/associate/<ip>", methods=["POST"])
def associateip(ip):
    resp = {}
    try:
        rqd = request.get_data()
        data = json.loads(rqd)
    except:
        application.logger.warn("Unable to parse pull data '%s'" % (rqd))
        return not_found(error='Bad data block')
    try:
        authstr = request.headers.get(AUTH_HEADER)
        session = auth_handler.authenticate(authstr)
        if not is_allowed(session):
            return unauthorized()
        session['ip'] = ip
        address = router.associate(session, data)
    except:
        return not_found()

    resp['address'] = address
    return jsonify(resp)


@application.route("/v1/release/")
def release():
    resp = {}
    try:
        authstr = request.headers.get(AUTH_HEADER)
        session = auth_handler.authenticate(authstr)
        if not is_allowed(session):
            return unauthorized()
        status = router.release(session['ip'])
    except:
        return not_found()

    resp['status'] = status
    return jsonify(resp)


@application.route("/v1/release/<ip>")
def releaseip(ip):
    resp = {}
    try:
        authstr = request.headers.get(AUTH_HEADER)
        session = auth_handler.authenticate(authstr)
        if not is_allowed(session):
            return unauthorized()
        status = router.release(ip)
    except:
        return not_found()

    resp['status'] = status
    return jsonify(resp)


@application.route("/v1/addresses/")
def list_addresses():
    resp = {}
    try:
        authstr = request.headers.get(AUTH_HEADER)
        session = auth_handler.authenticate(authstr)
        if not is_allowed(session):
            return unauthorized()
        addrs = router.available()
    except:
        return not_found()

    resp['available'] = addrs
    return jsonify(resp)


@application.route("/v1/status/")
def status():
    status = {}
    try:
        authstr = request.headers.get(AUTH_HEADER)
        session = auth_handler.authenticate(authstr)
        if not is_allowed(session):
            return unauthorized()
        status = router.status()
    except:
        return not_found()
    return jsonify({'data': status})


if __name__ == "__main__":
    application.run(host='0.0.0.0')
