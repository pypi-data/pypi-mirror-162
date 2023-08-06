import yaml

def read_yaml_file(path: str) -> dict:
    """
    Reads a file and returns its contents.
    """
    try:
        with open(path, "r") as file:
            parsed_yaml = yaml.safe_load(file)
            return parsed_yaml
    except FileNotFoundError as e:
        # print("File not found: " + path)
        return None


def write_yaml_file(path: str, data: dict) -> bool:
    try:
        with open(path, "w") as file:
            yaml.dump(data, file, sort_keys=False, default_flow_style=False)
            return True
    except Exception as e:
        return False