from flask import jsonify
from dtbase.core.structure import SQLA as db


def add_default_session(func):
    """Decorator for adding a default value of db.session for the `session` argument."""

    def new_func(*args, session=None, **kwargs):
        if session is None:
            session = db.session
        return func(*args, session=session, **kwargs)

    return new_func


def check_keys(payload, keys, api_endpoint):
    """Check if `keys` are in `payload` and return a json response if not.
    
    Args:
        payload: Dictionary to check.
        keys: List required keys to check for.
        api_endpoint: API endpoint that was called.
    
    Returns:
        None if all keys are in payload, otherwise a json response with an error.
    """
    
    missing = [k for k in keys if k not in payload.keys()]
    if missing:
        return (
            jsonify({"error": f"Must include {missing} in POST request to {api_endpoint}."}),
            400,
        )
    return None