"""
Ref: https://github.com/Torantulino/Auto-GPT/blob/master/scripts/json_parser.py
"""

import json
import re
from typing import Any, Dict, Union

from .call_ai_function import call_ai_function
from .config import Config
from .json_utils import correct_json
from .utils import get_logger

logger = get_logger(__name__)


cfg = Config()

JSON_SCHEMA = """
{
        "id": "be0b2a5e.82f9a8",
        "type": "tab",
        "label": "IoT Camera Streaming",
        "disabled": false,
        "info": ""
    },
    {
        "id": "7f5aa02c.f2075",
        "type": "inject",
        "z": "be0b2a5e.82f9a8",
        "name": "Add Device",
        "topic": "",
        "payload": "{\"device\": \"IoT Device 1\"}",
        "payloadType": "json",
        "repeat": "",
        "crontab": "",
        "once": false,
        "onceDelay": 0.1,
        "x": 140,
        "y": 100,
        "wires": [
            [
                "e1c7ded6.04d39"
            ]
        ]
    },
    {
        "id": "e1c7ded6.04d39",
        "type": "function",
        "z": "be0b2a5e.82f9a8",
        "name": "Add Device",
        "func": "",
        "outputs": 1,
        "noerr": 0,
        "x": 300,
        "y": 100,
        "wires": [
            [
                "2c5b5eaf.2e5f5c"
            ]
        ]
    },
    {
        "id": "2c5b5eaf.2e5f5c",
        "type": "debug",
        "z": "be0b2a5e.82f9a8",
        "name": "Device Added",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "statusVal": "",
        "statusType": "auto",
        "x": 510,
        "y": 100,
        "wires": []
    }
}
"""


def fix_and_parse_json(
    json_str: str,
    try_to_fix_with_gpt: bool = True
) -> Union[str, Dict[Any, Any]]:
    json_str = json_str.strip()

    """Fix and parse JSON string"""
    try:
        json_str = json_str.replace('\t', '')

        if "```" in json_str:
            if "```json" in json_str:
                json_str = json_str.replace("```json", "```")
            code_blocks = re.findall("```(.+?)```", json_str, re.DOTALL)
            if len(code_blocks) > 1:
                raise ValueError("More than one code block found")
            json_str = code_blocks[0]

        return json.loads(json_str)
    except json.JSONDecodeError as _:  # noqa: F841
        try:
            json_str = correct_json(json_str)
            return json.loads(json_str)
        except json.JSONDecodeError as _:  # noqa: F841
            pass
    # Let's do something manually:
    # sometimes GPT responds with something BEFORE the braces:
    # "I'm sorry, I don't understand. Please try again."
    # {"text": "I'm sorry, I don't understand. Please try again.",
    #  "confidence": 0.0}
    # So let's try to find the first brace and then parse the rest
    #  of the string
    try:
        brace_index = json_str.index("{")
        json_str = json_str[brace_index:]
        last_brace_index = json_str.rindex("}")
        json_str = json_str[:last_brace_index+1]
        return json.loads(json_str)
    # Can throw a ValueError if there is no "{" or "}" in the json_str
    except (json.JSONDecodeError, ValueError) as e:  # noqa: F841
        if try_to_fix_with_gpt:
            logger.warn("Warning: Failed to parse AI output, attempting to fix."
                        "\n If you see this warning frequently, it's likely that"
                        " your prompt is confusing the AI. Try changing it up"
                        " slightly.")
            # Now try to fix this up using the ai_functions
            ai_fixed_json = fix_json(json_str, JSON_SCHEMA)

            if ai_fixed_json != "failed":
                return json.loads(ai_fixed_json)
            else:
                # This allows the AI to react to the error message,
                #   which usually results in it correcting its ways.
                logger.error("Failed to fix AI output, telling the AI.")
                return json_str
        else:
            raise e


def fix_json(json_str: str, schema: str) -> str:
    """Fix the given JSON string to make it parseable and fully compliant with the provided schema."""
    # Try to fix the JSON using GPT:
    function_string = "def fix_json(json_str: str, schema:str=None) -> str:"
    args = [f"'''{json_str}'''", f"'''{schema}'''"]
    description_string = "Fixes the provided JSON string to make it parseable"\
        " and fully compliant with the provided schema.\n If an object or"\
        " field specified in the schema isn't contained within the correct"\
        " JSON, it is omitted.\n This function is brilliant at guessing"\
        " when the format is incorrect."

    # If it doesn't already start with a "`", add one:
    if not json_str.startswith("`"):
        json_str = "```json\n" + json_str + "\n```"
    result_string = call_ai_function(
        function_string, args, description_string, model=cfg.fast_llm_model
    )
    logger.debug("------------ JSON FIX ATTEMPT ---------------")
    logger.debug(f"Original JSON: {json_str}")
    logger.debug("-----------")
    logger.debug(f"Fixed JSON: {result_string}")
    logger.debug("----------- END OF FIX ATTEMPT ----------------")

    try:
        json.loads(result_string)  # just check the validity
        return result_string
    except:  # noqa: E722
        # Get the call stack:
        # import traceback
        # call_stack = traceback.format_exc()
        # print(f"Failed to fix JSON: '{json_str}' "+call_stack)
        return "failed"
