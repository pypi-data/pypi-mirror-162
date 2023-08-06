from kubiya import actions_store
from kubiya.http import serve
from kubiya.loader import load_actions_store
from sys import argv, exit

def serve_all(filename=None):
    instances = actions_store.ActionsStore._instances
    if not instances:
        print("No stores found")
        exit(1)
    if len(instances) > 1:
        print("Multiple stores found: {instances}")
        exit(1)
    serve(instances[0], filename)

if __name__ == "__main__":    
    if len(argv) != 2:
        print("Usage: python3 -m kubiya.serve <actions_store_file.py>")
        exit(1)
    
    store_file = load_actions_store(argv[1])
    serve_all(store_file)