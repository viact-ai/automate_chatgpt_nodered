import json
import os
import traceback

import dotenv
import openai
import requests

dotenv.load_dotenv()


openai.api_key = os.getenv("OPENAI_API_KEY", "")
assert openai.api_key != "", "Key for OPENAI API is empty"

NODE_RED_SERVER = os.getenv("NODE_RED_SERVER", "")
assert NODE_RED_SERVER != "", "NODE_RED_SERVER is empty"


def gen_id():
    import uuid
    return str(uuid.uuid4()).replace("-", ".")


def gpt_wrapper_function(prompt, texts, *args, **kargs):
    content = prompt.format(*texts).strip()
    print(content)
    response = openai.ChatCompletion.create(
        *args,
        model='gpt-3.5-turbo',
        messages=[
            {"role": "user", "content": content},
        ],
        **kargs,
    )

    """
    {
        'id': 'chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve',
        'object': 'chat.completion',
        'created': 1677649420,
        'model': 'gpt-3.5-turbo',
        'usage': {'prompt_tokens': 56, 'completion_tokens': 31, 'total_tokens': 87},
        'choices': [
            {
                'message': {
                    'role': 'assistant',
                    'content': 'The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers.'},
                'finish_reason': 'stop',
                'index': 0
            }
        ]
    }
    """

    return response['choices'][0]['message']['content']


def gpt_generate_node_red_flow(requirements):
    resp = gpt_wrapper_function(
        prompt="""
        Generate node-red code that:\n
        {}\n
        Notice to the syntax, just return json code, do not write explanations.
        """,
        texts=[requirements],
        temperature=0.9,
    )
    return resp


def create_node_red_flow(json_flow):
    try:
        headers = {
            "Content-Type": "application/json",
            "Node-RED-API-Version": "v2",
            "Node-RED-Deployment-Type": "full",
        }
        resp = requests.post(
            f"{NODE_RED_SERVER}/flows",
            data=json.dumps(json_flow),
            headers=headers,
        )
        return resp
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        raise Exception("Cannot create node-red flow")


def get_flow_id(json_flow):
    tmp = list(filter(lambda x: x['type'] == 'tab', json_flow['flows']))
    if len(tmp) != 0:
        return tmp[0]['id']

    tmp = list(filter(lambda x: 'z' in x, json_flow['flows']))
    if len(tmp) != 0:
        return tmp[0]['z']


def create_flow_id(json_flow):
    tmp = list(filter(lambda x: x['type'] == 'tab', json_flow['flows']))
    if len(tmp) == 0:

        flow_id = gen_id()
        json_flow['flows'].append({
            'id': flow_id,
            'type': 'tab',
            'label': 'Generated Flow',
        })
        for idx, flow in enumerate(json_flow['flows']):
            flow['z'] = flow_id
            json_flow['flows'][idx] = flow

    return flow_id, json_flow


if __name__ == "__main__":
    print(gpt_generate_node_red_flow(
        "Add IoT devices\nConnect cameras to IoT that device\nstream signal to internet via RTSP\nselect an AI engine in the IoT device to process the data from connected cameras\nsend the alert through telegram whenever AI engine output is detected\nsend the alert through email whenever the iot device output is overload"))
