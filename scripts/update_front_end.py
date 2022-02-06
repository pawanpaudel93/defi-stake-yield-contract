import yaml
import json


def main():
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
    with open("brownie-config.json", "w") as brownie_config:
        json.dump(config_dict, brownie_config, indent=4)
    print("Updated brownie-config.json")
