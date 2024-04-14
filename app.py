import json
import logging

import requests
import websockets
from config import REDIS_URL, WEBSOCKET_URL, Config
from flask import Flask, jsonify
from redis import Redis

app = Flask(__name__)
app.config.from_object(Config)

redis = Redis.from_url(REDIS_URL, encoding='utf-8', decode_responses=True)

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='./errors.log')


def get_coins_list(start):
    url = "https://api.coinmarketcap.com/aggr/v3/web/homepage"
    payload = {
        "start": start,
        "limit": 100
    }
    response = requests.get(url, params=payload).json()
    if response["status"]["error_code"] != "0":
        return []
    return response["data"]["listing"]["cryptoCurrencyList"]


def get_coin_by_symbol(symbol):
    url = "https://api.coinmarketcap.com/gravity/v4/gravity/global-search"
    payload = {
        "keyword": symbol,
        "scene": "community",
        "limit": 5
    }
    response = requests.post(url, json=payload).json()
    if response["status"]["error_code"] != "0":
        return []
    response = [i for i in response["data"]["suggestions"] if i["type"] == "token"]
    if not response:
        return None
    response = response[0]["tokens"]
    return response[0]


@app.route('/coins')
@app.route('/coins/')
async def get_list():
    results = []
    s = 1
    limit = 100
    while True:
        res = get_coins_list(s)
        if not res:
            break
        for item in res:
            if item["symbol"] not in results:
                results.append(item["symbol"])
        s += limit
    return jsonify({"ok": True, "results": results}), 200


@app.route('/<string:symbol>')
@app.route('/<string:symbol>/')
async def get_price(symbol):
    coin = get_coin_by_symbol(symbol)
    if not coin:
        return jsonify({"ok": False, "result": "symbol not found."}), 404
    price = 0
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await websocket.send(json.dumps({
            "method": "RSUBSCRIPTION",
            "params": ["main-site@crypto_price_15s@{}@detail", str(coin["id"])]
        }))
        await websocket.send(json.dumps({
            "method": "RSUBSCRIPTION",
            "params": ["main-site@crypto_price_5s@{}@normal", str(coin["id"])]
        }))
        while True: 
            response = await websocket.recv()
            response = json.loads(response)
            if response.get("d"):
                price = response["d"]["p"]
                break
    return jsonify({"ok": True, "result": price}), 200

