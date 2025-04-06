from flask import jsonify

def success(data: dict, code=200):
    return jsonify({
        "status": "success",
        "code": code,
        "data": data,
        "error": None
    }), code

def error(message: str, code=400):
    return jsonify({
        "status": "error",
        "code": code,
        "data": None,
        "error": message
    }), code
