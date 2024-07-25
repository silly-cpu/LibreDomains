import json
import os
import sys

def validate_json(file_path):
    with open(file_path, 'r') as file:
        try:
            data = json.load(file)
            required_keys = {"record", "type", "content", "ttl"}
            if not required_keys.issubset(data.keys()):
                print(f"Error: {file_path} is missing required keys.")
                return False
        except json.JSONDecodeError as e:
            print(f"Error: {file_path} is not a valid JSON file. {e}")
            return False
    return True

def main():
    subdomains_dir = 'subdomains'
    for filename in os.listdir(subdomains_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(subdomains_dir, filename)
            if not validate_json(file_path):
                sys.exit(1)
    print("All JSON files are valid.")
    sys.exit(0)

if __name__ == "__main__":
    main()