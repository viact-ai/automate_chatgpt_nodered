import json

import utils


def main():
    json_flow = json.load(open('sample_result.json'))
    print(utils.create_node_red_flow(json_flow))


if __name__ == "__main__":
    main()
