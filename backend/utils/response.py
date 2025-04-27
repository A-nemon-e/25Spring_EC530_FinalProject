from flask import jsonify

def success(data: dict, code=200):
    """
    Create a standardized success response.

    Args:
        data (dict): The response payload.
        code (int, optional): HTTP status code. Defaults to 200.

    Returns:
        tuple: A Flask response object and the HTTP status code.

    Example:
        >>> from utils.response import success
        >>> response = success({"id": 123})
    """
    return jsonify({
        "status": "success",
        "code": code,
        "data": data,
        "error": None
    }), code

def error(message: str, code=400):
    """
    Create a standardized error response.

    Args:
        message (str): Error message description.
        code (int, optional): HTTP status code. Defaults to 400.

    Returns:
        tuple: A Flask response object and the HTTP status code.

    Example:
        >>> from utils.response import error
        >>> response = error("Invalid input", code=422)
    """
    return jsonify({
        "status": "error",
        "code": code,
        "data": None,
        "error": message
    }), code
