import json
import logging
import sys

import streamlit as st

import utils

# create logger that log to file and stdout with the same format
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
shandler = logging.StreamHandler(sys.stdout)
shandler.setFormatter(formatter)
logger.addHandler(shandler)

fhandler = logging.FileHandler("app.log")
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)


def main():
    st.title("Gereate Node-RED flow")
    requirements = st.text_area("Requirements")
    if st.button("Generate"):
        placeholder = st.empty()
        with placeholder.container():
            with st.spinner("Generating..."):
                json_txt = utils.gpt_generate_node_red_flow(requirements)

            try:
                json_data = json.loads(json_txt)
            except json.JSONDecodeError:
                st.error("Cannot generate flow, please try again")
                logger.error("Cannot generate flow, please try again")
                logger.error(f"Returned json: {json_txt}")
                return

            if isinstance(json_data, list):
                json_data = {
                    "flows": json_data,
                }

            logger.info(f"Generated json: {json.dumps(json_data, indent=4)}")

            flow_id = utils.get_flow_id(json_data)

            if flow_id is None:
                flow_id, json_data = utils.create_flow_id(json_data)
                logger.info(f"Created flow id: {flow_id}")
                logger.info(f"After gen: {json.dumps(json_data, indent=4)}")

            resp = utils.create_node_red_flow(json_data)
            if resp.status_code != 200:
                st.error("Cannot generate flow, please try again")
                logger.error("Cannot generate flow, please try again")
                logger.error(f"Status code: {resp.status_code}")
                return

            logger.info(f"Rev id: {resp.json()['rev']}")
            logger.info(f"Flow id: {flow_id}")

            st.markdown("""
                <a href="{}" target="_blank">Open node-red flow</a>
                """.format(f"{utils.NODE_RED_SERVER}/#flow/{flow_id}"), unsafe_allow_html=True)


if __name__ == "__main__":
    main()