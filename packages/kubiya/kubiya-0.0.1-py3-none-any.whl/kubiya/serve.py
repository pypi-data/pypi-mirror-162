from kubiya import kubiya_integration
from kubiya.http import serve
from kubiya.loader import load_integration
from sys import argv, exit

def serve_all(filename=None):
    instances = kubiya_integration.KubiyaIntegraion._instances
    if not instances:
        print("No integrations found")
        exit(1)
    if len(instances) > 1:
        print("Multiple integrations found: {instances}")
        exit(1)
    serve(instances[0], filename)

if __name__ == "__main__":    
    if len(argv) != 2:
        print("Usage: python3 -m kubiya.serve <integration>")
        exit(1)
    
    integration_file = load_integration(argv[1])
    serve_all(integration_file)