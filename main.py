from flask import Flask, jsonify
from flask_caching import Cache
import config as CONFIG

import pydexcom

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

app = Flask(__name__)
cache.init_app(app)



@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/v1/bloodsugar")
def bloodsugar():
    return "<p>Hello, World!</p>"


@app.route("/config")
def client_config():
    config = {
        "low_alert_range": CONFIG.LOW_ALERT_RANGE,
        "high_alert_range": CONFIG.HIGH_ALERT_RANGE,
    }
    return jsonify(config)
