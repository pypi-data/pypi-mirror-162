import logging

import pydng
from flask import Flask, jsonify

_log = logging.getLogger(__name__)

app = Flask(__name__)


def username_exists(username):
    from .store import create

    try:
        user_id = create().load(username).get_id()
        return username == user_id
    except AttributeError:
        return False


@app.route("/generated_username")
def get_generated_username():
    # use additional random integer to increase possible combinations
    # import random
    # new_username = f"{pydng.generate_name()}_{random.randint(1, 10)}"

    new_username = pydng.generate_name()  # 108 adjectives * 237 lastnames = 25.596 combinations

    if username_exists(new_username):
        _log.info(f"Generated user {new_username} already exists. Retrying...")
        return get_generated_username()

    return jsonify(new_username)


def create():
    return app
