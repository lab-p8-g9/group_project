import json


class json_handling:

    def __init__(self, ai_file):
        self.__ai_file = ai_file

    def read(self):

        try:
            with open(self.__ai_file, "r", encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError:
            print(f"File not found: {self.__ai_file}")
            raise

        except json.JSONDecodeError:
            print(f"Invalid JSON format: {self.__ai_file}")
            raise

        except OSError as error:
            print(f"File reading error: {error}")
            raise

    def clear(self):

        try:
            with open(self.__ai_file, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)

        except OSError as error:
            print(f"File clearing error: {error}")
            raise