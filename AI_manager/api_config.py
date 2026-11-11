import os
from dotenv import load_dotenv, find_dotenv

class APIConfig:
    def __init__(self):
        # Load environment variables
        #load_dotenv(find_dotenv())

        #Get the directory where api_config.py lives (the AI_manager folder)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Go one level up to get the root directory (the group_project folder)
        root_dir = os.path.dirname(current_dir)
        
        # Build the exact absolute path to the .env file
        env_path = os.path.join(root_dir, '.env')
        
        load_dotenv(dotenv_path=env_path)
        
        # Fetch the api key
        self.api_key = os.getenv("OPENROUTER_API_KEY")  #get your own api key from openrouter and insert into .env

        self.base_url = "https://openrouter.ai/api/v1"
        self.timeout = 15.0 #triggers timeout error if no response within 15 seconds
        
        # Validate it immediately so the program crashes early if the key is missing
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing from the .env file!")