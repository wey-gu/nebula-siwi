import os

from flask import Flask, jsonify, request
from nebula2.gclient.net import ConnectionPool
from nebula2.Config import Config
from siwi.bot import bot


app = Flask(__name__)


@app.route("/")
def root():
    return "Hey There?"


@app.route("/query", methods=["POST"])
def query():
    request_data = request.get_json()
    question = request_data.get("question", "")
    if question:
        answer = siwi_bot.query(request_data.get("question", ""))
    else:
        answer = "Sorry, what did you say?"
    return jsonify({"answer": answer})


def parse_nebula_graphd_endpoint():
    ng_endpoints_str = os.environ.get(
        'NG_ENDPOINTS', '127.0.0.1:9669,').split(",")
    ng_endpoints = []
    for endpoint in ng_endpoints_str:
        if endpoint:
            parts = endpoint.split(":")  # we dont consider IPv6 now
            ng_endpoints.append((parts[0], int(parts[1])))
    return ng_endpoints


ng_config = Config()
ng_config.max_connection_pool_size = int(
    os.environ.get('NG_MAX_CONN_POOL_SIZE', 10))
ng_endpoints = parse_nebula_graphd_endpoint()
connection_pool = ConnectionPool()

if __name__ == "__main__":
    connection_pool.init(ng_endpoints, ng_config)
    siwi_bot = bot.SiwiBot(connection_pool)
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        connection_pool.close()
else:
    connection_pool.init(ng_endpoints, ng_config)
    siwi_bot = bot.SiwiBot(connection_pool)
