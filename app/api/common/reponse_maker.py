from flask import make_response, jsonify


def response_maker(body, status_code):
    return make_response(jsonify(body), status_code)
