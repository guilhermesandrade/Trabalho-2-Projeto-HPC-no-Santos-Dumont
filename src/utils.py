import os, json, time

def timestamp():
    return int(time.time())

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def save_json(path, obj):
    ensure_dir(os.path.dirname(path) or '.')
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)
