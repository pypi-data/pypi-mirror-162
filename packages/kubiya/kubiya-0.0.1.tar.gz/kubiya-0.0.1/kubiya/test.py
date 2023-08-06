from kubiya import kubiya_integration
from kubiya.loader import load_integration
from sys import argv, exit

def serve_all():
    instances = kubiya_integration.KubiyaIntegraion._instances
    if not instances:
        print("No integrations found")
        exit(1)
    if len(instances) > 1:
        print("Multiple integrations found: {instances}")
        exit(1)
    for instance in instances:
        print(f"{instance.get_name()}:")
        for action in instance.get_registered_actions():
            print(f"  {action}")

if __name__ == "__main__":    
    if len(argv) != 2:
        print("Usage: python3 -m kubiya.serve <integration>")
        exit(1)
    
    load_integration(argv[1])
    serve_all()