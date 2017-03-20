#!/usr/bin/python

import pprint
from flask import Flask, jsonify, request
import router

application = Flask(__name__)
pp = pprint.PrettyPrinter(indent=4)

router = router.Router()


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


@application.route("/associate/<nid>")
def associate(nid):
    resp = {}
    try:
        address = router.associate(int(nid))
    except:
        return not_found()

    resp['address'] = address
    return jsonify(resp)


@application.route("/release/<nid>")
def release(nid):
    resp = {}
    try:
        status = router.release(int(nid))
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
