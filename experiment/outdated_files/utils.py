import json

def load_json(fpath):
    with open(fpath, 'r') as f:
        res = json.load(f)
        return res
