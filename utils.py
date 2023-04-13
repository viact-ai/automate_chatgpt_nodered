import ast
import json
import os
import re
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
    try:
        tmp = list(filter(lambda x: x['type'] == 'tab', json_flow['flows']))
        if len(tmp) != 0:
            return tmp[0]['id']

        tmp = list(filter(lambda x: 'z' in x, json_flow['flows']))
        if len(tmp) != 0:
            return tmp[0]['z']
    except Exception as e:
        print(json_flow)
        print(f"Error: {e}")
        print(traceback.format_exc())
        raise Exception("Cannot get flow id")


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


# def fix_json_with_js_code(json_string):
#     # Check if the string is already valid JSON
#     try:
#         parsed_json = json.loads(json_string)
#         return parsed_json
#     except json.JSONDecodeError:
#         pass

#     # Define a regular expression to match JavaScript code blocks
#     js_code_regex = re.compile(
#         r'(?<!\\)"((?<!\\)\\(?!n|r|t|u)|(?<!\\)(?s:.)*?(?<!\\))(?<!\\)"')

#     # Replace JavaScript code blocks with escaped versions
#     def escape_js_code(match):
#         code = match.group(1)
#         return '"' + code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
#     fixed_json = js_code_regex.sub(escape_js_code, json_string)

#     # Parse the fixed JSON string
#     parsed_json = json.loads(fixed_json)
#     return parsed_json

def correct_json(json_str):
    try:
        # Try to parse the JSON string as is
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # If parsing failed, try to correct any syntax errors in the JavaScript code
    json_str = json_str.replace('\n', ' ')  # Remove any newlines
    parsed_json = ''

    # Parse the JSON string one character at a time
    for i, c in enumerate(json_str):
        parsed_json += c
        try:
            # Try to parse the resulting string as an abstract syntax tree
            ast.parse(parsed_json)
            # If parsing succeeded, we're done
            return json.loads(parsed_json)
        except SyntaxError:
            # If parsing failed, continue parsing until we find the error
            pass


def extract_code_blocks_from_md(md_string):
    try:
        return [json.loads(md_string)]
    except Exception as e:
        pass

    # Find all code blocks
    code_blocks = re.findall("```(.+?)```", md_string, re.DOTALL)
    if len(code_blocks) == 0:
        try:
            return [json.loads(md_string)]
        except Exception as e:
            pass

        try:
            return correct_json(md_string)
        except Exception as e:
            return

    for i in range(len(code_blocks)):
        try:
            code_blocks[i] = correct_json(code_blocks[i])
        except Exception as e:
            print(f"Error: {e}")
            print(traceback.format_exc())

    return code_blocks


def process_code_blocks(code_blocks):
    if len(code_blocks) == 0:
        return

    if len(code_blocks) == 1:
        if isinstance(code_blocks[0], list):
            return {
                "flows": code_blocks[0],
            }

    flows = []
    for block in code_blocks:
        if isinstance(block, list):
            flows += block
        else:
            flows.append(block)

    return {
        "flows": flows,
    }


if __name__ == "__main__":
    print(gpt_generate_node_red_flow(
        "Add IoT devices\nConnect cameras to IoT that device\nstream signal to internet via RTSP\nselect an AI engine in the IoT device to process the data from connected cameras\nsend the alert through telegram whenever AI engine output is detected\nsend the alert through email whenever the iot device output is overload"))
