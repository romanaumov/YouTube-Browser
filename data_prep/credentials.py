import os
import json

# Examples of the Amazon Application Credentials - filepath "./config/AMAZON_APPLICATION_CREDENTIALS.json"
# AWS_ACCESS_KEY_ID="your_access_key"
# AWS_SECRET_ACCESS_KEY="your_secret_access_key"
# AWS_DEFAULT_REGION="your_region"

# Path to your JSON file containing credentials
aws_credentials_path = "./config/AMAZON_APPLICATION_CREDENTIALS.json"

# AWS credentials
def set_aws_credentials_from_json(path):
    try:
        # Load the JSON file
        with open(path, 'r') as json_file:
            credentials = json.load(json_file)

        # Set environment variables from the JSON data
        os.environ["AWS_ACCESS_KEY_ID"] = credentials["AWS_ACCESS_KEY_ID"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = credentials["AWS_SECRET_ACCESS_KEY"]
        os.environ["AWS_DEFAULT_REGION"] = credentials["AWS_DEFAULT_REGION"]

        print("AWS credentials have been set successfully.")
    except FileNotFoundError:
        print(f"Error: The file {path} was not found.")
    except KeyError as e:
        print(f"Error: Missing key in the JSON file: {e}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
