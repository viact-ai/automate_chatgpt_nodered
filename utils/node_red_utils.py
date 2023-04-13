import json

import requests

from .config import Config
from .llm_utils import create_chat_completion
from .utils import get_logger

cfg = Config()

logger = get_logger(__name__)


def create_node_red_flow(json_flow):
    try:
        headers = {
            "Content-Type": "application/json",
            "Node-RED-API-Version": "v2",
            "Node-RED-Deployment-Type": "full",
        }
        resp = requests.post(
            f"{cfg.node_red_server}/flows",
            data=json.dumps(json_flow),
            headers=headers,
        )
        return resp
    except Exception as e:
        logger.exception(e)
        # raise Exception("Cannot create node-red flow")


def generate_node_red_flow(requirements):
    resp_txt = create_chat_completion(
        messages=[
            {"role": "system", "content": "You are now a node-red flow generator that could generate up to 2000 tokens"},
            {"role": "user", "content": f"Generate node-red code that:\n{requirements}\nReturn json code only."},
        ],
        model="gpt-3.5-turbo",
        temperature=0.9,
    )
    return resp_txt


def generate_random_id(n=10):
    """Generate random string with n characters"""
    import random
    import string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


def correct_json_flow(json_data):
    """Try to convert json to node-red v2 format"""
    if isinstance(json_data, list):
        json_data = {
            "flows": json_data,
        }

    tab_nodes = [node for node in json_data["flows"] if node["type"] == "tab"]
    flow_id = None
    if len(tab_nodes) == 0:
        flow_id = generate_random_id()
        json_data["flows"].insert(
            0,
            {
                "id": flow_id,
                "type": "tab",
                "label": "ChatGPT Generated Flow",
            },
        )

        for node in json_data["flows"]:
            if node["type"] != "tab":
                node["z"] = flow_id
    else:
        flow_id = tab_nodes[0]["id"]

    return json_data, flow_id
