from flask import Flask, jsonify
from flask_caching import Cache
from datetime import datetime, timezone
import config as CONFIG

from pydexcom import Dexcom


cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

app = Flask(__name__)
cache.init_app(app)


@app.route("/v1/bloodsugar")
def bloodsugar():
    bloodsugar = get_bloodsugar()
    
    # Make the esp32 process easier, calculate how long it needs to sleep before it pulls again
    now = datetime.now(timezone.utc)
    delta_seconds = (now - bloodsugar.datetime).total_seconds()
    seconds_remaining =  300 - delta_seconds  # 5 minute delta
    
    json_response = {
        "value": bloodsugar.value,
        "datetime": bloodsugar.datetime.isoformat(),
        "trend": bloodsugar.trend,
        "trend_arrow": bloodsugar.trend_arrow,
        "update_seconds_remaining": seconds_remaining,
        "disable_alerting": False,
    }
    # Return if it's in the alerting threshold timeframe
    return jsonify(json_response)


@app.route("/config")
def client_config():
    config = {
        "low_alert_range": CONFIG.LOW_ALERT_RANGE,
        "high_alert_range": CONFIG.HIGH_ALERT_RANGE,
    }
    return jsonify(config)


def get_bloodsugar():
    cached_reading = cache.get('glucose_reading')

    # Check cache data
    if cached_reading is not None:
        now = datetime.now(timezone.utc)
        delta_seconds = (now - cached_reading.datetime).total_seconds()
        if delta_seconds < 280: # Just under 5 minutes
            print(f"Using cached reading: {cached_reading.value} at {cached_reading.datetime}")
            return cached_reading
    
    # Cache is empty or too old, fetch new data
    dexcom = get_dexcom()
    glucose_reading = dexcom.get_current_glucose_reading()

    if 10 <= glucose_reading.value <= 1000:
        cache.set('glucose_reading', glucose_reading)

    cache.set('dexcom', dexcom)
    return glucose_reading

def get_dexcom():
    dexcom = cache.get('dexcom')
    if dexcom is None:
        return dexcom_init()
    
    return dexcom

def dexcom_init():
    dexcom = Dexcom(username=CONFIG.DEXCOM_USERNAME, password=CONFIG.DEXCOM_PASSWORD)
    cache.set('dexcom', dexcom)
    return dexcom