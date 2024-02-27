import yaml
import json
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

dynamodb_endpoint = os.getenv('DYNAMODB_ENDPOINT')

def batch_write(table_name, batch_items):
    command = [
        "aws", "dynamodb", "batch-write-item",
        "--request-items", json.dumps({table_name: batch_items}),
        "--endpoint-url", dynamodb_endpoint
    ]
    subprocess.run(command, check=True)

def load_items_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def prepare_items_for_batch_write(source_files):
    items = []
    for file_path in source_files:
        modified_path = f"./schema/seeds/.build/{file_path}"
        loaded_items = load_items_from_file(modified_path)
        items.extend(loaded_items)
    return items

def load_seeds():
    with open("./schema/seeds.yml", 'r') as file:
        config = yaml.safe_load(file)
        
        with ThreadPoolExecutor() as executor:
            futures = []
            for entry in config:
                table_name = entry['table']
                source_files = entry['sources']
                items = prepare_items_for_batch_write(source_files)
                
                for i in range(0, len(items), 25):
                    batch_items = items[i:i+25]
                    futures.append(executor.submit(batch_write, table_name, batch_items))
            
            for future in futures:
                future.result()
                print(f"Seeded items to {table_name}.")

if __name__ == "__main__":
    load_seeds()
