import json
import os

# Save json file
def save_json(data, path):
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Save data to a JSON file
        with open(path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
            print(f"JSON data was saved to {path}.")

    except FileNotFoundError:
        return f"File {path} not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Read json file
def read_json(path):
    try:
        # Open JSON file
        with open(path, 'r') as file:
            data = json.load(file)
            print(f"JSON file was read successfully from {path} ")
        return data

    except FileNotFoundError:
        return f"File {path} not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"
