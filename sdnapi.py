#!/usr/bin/python

import pprint
from flask import Flask, jsonify, request
import router
import auth
import os

application = Flask(__name__)
pp = pprint.PrettyPrinter(indent=4)
application.config['DBHOST'] = 'localhost'
application.config['RTRUSER'] = 'sdn'
application.config['MAPFILE'] = './mapfile'
application.config['AUTHMODE'] = 'munge'

if 'SDN_SETTINGS' in os.environ:
    application.logger.info("Loading settings from " +
                            os.environ['SDN_SETTINGS'])
    application.config.from_envvar('SDN_SETTINGS')

application.logger.info(application.config)
print application.config

router = router.Router(application.config)

auth_mode = application.config['AUTHMODE']
auth_handler = auth.Authentication({'authentication': auth_mode})
AUTH_HEADER = 'authentication'


@application.route("/")
def hello():
    return "/{associate,release}"


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


@application.route("/_ping")
def ping():
    return ''


@application.route("/associate/")
def associate():
    resp = {}
    try:
        authstr = request.headers.get(AUTH_HEADER)
        session = auth_handler.authenticate(authstr)
        address = router.associate(session)
    except:
        return not_found()

    resp['address'] = address
    return jsonify(resp)


@application.route("/associate/<ip>")
def associateip(ip):
    resp = {}
    try:
        authstr = request.headers.get(AUTH_HEADER)
        session = auth_handler.authenticate(authstr)
        if 'uid' not in session:
            raise ValueError("Missing UID")
        session['ip'] = ip
        address = router.associate(session)
    except:
        return not_found()

    resp['address'] = address
    return jsonify(resp)


@application.route("/release/")
def release():
    resp = {}
    try:
        authstr = request.headers.get(AUTH_HEADER)
        session = auth_handler.authenticate(authstr)
        status = router.release(session['ip'])
    except:
        return not_found()

    resp['status'] = status
    return jsonify(resp)


@application.route("/release/<ip>")
def releaseip(ip):
    resp = {}
    try:
        authstr = request.headers.get(AUTH_HEADER)
        session = auth_handler.authenticate(authstr)
        if 'uid' not in session:
            raise ValueError("Missing UID")
        status = router.release(ip)
    except:
        return not_found()

    resp['status'] = status
    return jsonify(resp)


@application.route("/addresses/")
def list_addresses():
    resp = {}
    try:
        addrs = router.available()
    except:
        return not_found()

    resp['available'] = addrs
    return jsonify(resp)


@application.route("/status/")
def status():
    resp = {}
    try:
        addrs = router.status()
    except:
        return not_found()

    resp['available'] = addrs
    return jsonify(resp)


if __name__ == "__main__":
    application.run(host='0.0.0.0')
