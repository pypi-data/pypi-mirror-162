import os
import json
import yaml
import requests
import tempfile
import shutil
import argparse


def find_config_cell(data: list) -> int:
    for idx, cell in enumerate(data):
        if is_config_cell(cell):
            return idx

    raise Exception("No config cell found")


def is_config_cell(cell: dict) -> bool:
    if cell["cell_type"] != "raw":
        return False

    for key in ["title", "format", "jupyter"]:
        if not contains_key(key, cell["source"]):
            return False

    return True


def contains_key(target: str, cell_content: list) -> bool:
    for cfg_value in cell_content:
        if cfg_value.split(":")[0] == target:
            return True

    return False


def get_config(cfg_cell: dict) -> dict:
    config = ""
    for line in cfg_cell["source"][1:-1]:
        config += line

    return yaml.safe_load(config)


def ensure_knada_default_values(config: dict):
    config["include"] = False

    try:
        config["format"]["html"]
    except KeyError:
        config["format"] = {
            "html": {
                "self-contained": True
            }
        }
    else:
        config["format"]["html"]["self-contained"] = True


def insert_updated_config(cfg_cell: dict, config: dict) -> None:
    cfg_str = yaml.safe_dump(config)
    cfg_parts = cfg_str.split("\n")
    cfg_parts = [cfg_part + "\n" for cfg_part in cfg_parts]
    cfg_parts.pop(-1)
    cfg_cell["source"] = ["---\n"] + cfg_parts + ["---\n"]


def create_html(data: dict) -> str:
    temp_dir = tempfile.mkdtemp()
    try:
        with open(f"{temp_dir}/file.ipynb", "w") as f:
            f.write(json.dumps(data))

        os.system(f"quarto render {temp_dir}/file.ipynb")

        with open(f"{temp_dir}/file.html", "r") as f:
            html = f.read()
    except:
        shutil.rmtree(temp_dir)
        raise

    shutil.rmtree(temp_dir)

    return html


# Create the parser
parser = argparse.ArgumentParser(description='List the content of a folder')

# Add the arguments
parser.add_argument('notebook',
                    metavar='notebook',
                    type=str,
                    help='the jupyter notebook file')

parser.add_argument('--host',
                    metavar='host',
                    type=str,
                    help='host for nada api')


def main():
    args = parser.parse_args()

    file = args.notebook
    if not file.endswith(".ipynb"):
        raise Exception("invalid input file provided (must be .ipynb file)")

    host = os.getenv("NADA_HOST", "https://nada.intern.nav.no")
    if args.host:
        host = args.host

    with open(file, "r") as f:
        data = json.loads(f.read())

    cfg_cell_num = find_config_cell(data["cells"])
    config = get_config(data["cells"][cfg_cell_num])
    ensure_knada_default_values(config)
    insert_updated_config(data["cells"][cfg_cell_num], config)
    html = create_html(data)

    res = requests.post(f"{host}/api/quarto",
                        json={"content": html})
    res.raise_for_status()

    print(res.json())


if __name__ == "__main__":
    main()
