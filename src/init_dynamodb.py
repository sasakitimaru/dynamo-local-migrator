from compile_json import convert_all_json_in_directory
from create_tables import create_tables
from load_seeds import load_seeds

def main():
    convert_all_json_in_directory("./schema/seeds", "./schema/seeds/.build")
    is_completed = create_tables()
    if is_completed:
        load_seeds()

if __name__ == "__main__":
    main()
