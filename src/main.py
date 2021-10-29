from nebula2.gclient.net import ConnectionPool
from nebula2.Config import Config
from siwi.app import parse_nebula_graphd_endpoint
from siwi.bot import bot


ng_config = Config()
ng_config.max_connection_pool_size = int(
    os.environ.get('NG_MAX_CONN_POOL_SIZE', 10))
ng_endpoints = parse_nebula_graphd_endpoint()
connection_pool = ConnectionPool()
connection_pool.init(ng_endpoints, ng_config)
siwi_bot = bot.SiwiBot(connection_pool)


def siwi_api(request):
    request_data = request.get_json()
    question = request_data.get("question", "")
    if question:
        answer = siwi_bot.query(request_data.get("question", ""))
    else:
        answer = "Sorry, what did you say?"
    return jsonify({"answer": answer})
