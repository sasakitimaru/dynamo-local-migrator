import json
import os
import glob

def convert_to_dynamodb_format(data, is_top_level=True):
    if isinstance(data, dict):
        if is_top_level:
            return {key: convert_to_dynamodb_format(value, False) for key, value in data.items()}
        else:
            return {"M": {key: convert_to_dynamodb_format(value, False) for key, value in data.items()}}
    elif isinstance(data, list):
        return {"L": [convert_to_dynamodb_format(item, False) for item in data]}
    elif isinstance(data, str):
        return {"S": data}
    elif isinstance(data, bool):
        return {"BOOL": data}
    elif isinstance(data, int) or isinstance(data, float):
        return {"N": str(data)}
    elif data is None:
        return {"NULL": True}
    elif isinstance(data, set):
        if all(isinstance(item, str) for item in data):
            return {"SS": list(data)}
        elif all(isinstance(item, int) or isinstance(item, float) for item in data):
            return {"NS": [str(item) for item in data]}
        else:
            raise ValueError("Unsupported set type")
    else:
        raise ValueError("Unsupported data type")

def convert_file_to_dynamodb_batchwrite_format(file_path, output_dir):
    with open(file_path, 'r') as file:
        data = json.load(file)

    converted_data = [{"PutRequest": {"Item": convert_to_dynamodb_format(item)}} for item in data]
    table_name = os.path.splitext(os.path.basename(file_path))[0]

    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, f"{table_name}.json")

    with open(output_file_path, 'w') as outfile:
        json.dump(converted_data, outfile, indent=2)

    print(f"File saved to {output_file_path}")
    
def convert_all_json_in_directory(input_dir, output_dir):
    json_files = glob.glob(os.path.join(input_dir, '*.json'))
    for file_path in json_files:
        convert_file_to_dynamodb_batchwrite_format(file_path, output_dir)

if __name__ == "__main__":
    convert_all_json_in_directory("./schema/seeds", "./schema/seeds/.build")