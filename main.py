import json

import streamlit as st

import utils.utils as utils
from utils.config import Config
from utils.json_parser import fix_and_parse_json
from utils.node_red_utils import (correct_json_flow, create_node_red_flow,
                                  generate_node_red_flow)

cfg = Config()


def main():
    logger = utils.get_logger(__name__)

    st.title("Gereate Node-RED flow")
    requirements = st.text_area(
        "Requirements/Steps in the flow that you want to create")

    # Trigger action click on button
    if st.button("Generate"):
        placeholder = st.empty()
        with placeholder.container():
            with st.spinner("Generating..."):
                resp_txt = generate_node_red_flow(requirements)
                logger.info(f"ChatGPT response: {resp_txt}")

            json_data = fix_and_parse_json(resp_txt)
            logger.info(
                f"JSON after parsed: {json.dumps(json_data, indent=4)}")

            json_data, flow_id = correct_json_flow(json_data)
            logger.info(f"Flow id: {flow_id}")
            logger.info(
                f"JSON after corrected: {json.dumps(json_data, indent=4)}")

            resp = create_node_red_flow(json_data)
            if resp is None or resp.status_code != 200:
                st.error("Error when add node-red flow, please try again")
                logger.error(f"Response status code: {resp.status_code}")
                return

            logger.info(f"Rev id: {resp.json()['rev']}")

            st.markdown("""
                <a href="{}" target="_blank">Open node-red flow</a>
                """.format(f"{cfg.node_red_server}/#flow/{flow_id}"), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
