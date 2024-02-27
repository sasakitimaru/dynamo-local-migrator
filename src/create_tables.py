import yaml
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

dynamodb_endpoint = os.getenv('DYNAMODB_ENDPOINT')

def create_command(action, table_name, options, endpoint_url):
    command = ["aws", "dynamodb", action, "--table-name", table_name] + options + ["--endpoint-url", endpoint_url]
    return command

def run_aws_command(command):
    completed_process = subprocess.run(command, check=True, stdout=subprocess.PIPE)
    return completed_process

def check_table_exists(table_name, endpoint_url):
    list_tables_command = ["aws", "dynamodb", "list-tables", "--endpoint-url", endpoint_url]
    result = run_aws_command(list_tables_command)
    if table_name in result.stdout.decode():
        return True
    return False

def exec_create_table_cmd(table):
    temp_filename = f"{table['TableName']}_temp.yaml"
    with open(temp_filename, 'w') as temp_file:
        table_definition = {key: value for key, value in table.items()}
        yaml.safe_dump({"TableName": table['TableName'], **table_definition}, temp_file)
    create_options = ["--cli-input-yaml", f"file://{temp_filename}"]
    create_table_command = create_command("create-table", table['TableName'], create_options, dynamodb_endpoint)
    run_aws_command(create_table_command)
    print(f"Table {table['TableName']} created successfully.")

def create_tables():
    with open("./schema/tables.yml", 'r') as file:
        tables = yaml.safe_load(file)['Tables']
        table_for_check_already_exist = tables[0]
        if check_table_exists(table_for_check_already_exist['TableName'], dynamodb_endpoint):
            print(f"Table already exists. Skipping migration.")
            return False
        with ThreadPoolExecutor(max_workers=len(tables)) as executor:
            executor.map(exec_create_table_cmd, tables)
        return True

if __name__ == "__main__":
    create_tables()
