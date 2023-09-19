import json


class JsonConfigLoader:
    def __init__(self):
        self.system_messages = self.load_json_file('D:/python/Quantum_HiveMind/hive/json_utils/system_messages.json')
        self.system_prompts = self.load_json_file('D:/python/Quantum_HiveMind/hive/json_utils/system_prompts.json')
        self.function_metadata = self.load_json_file('D:/python/Quantum_HiveMind/hive/json_utils/function_metadata.json')

    @staticmethod
    def load_json_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Oopsie! Couldn't find the file at {file_path}. 🙈")
            return None
        except json.JSONDecodeError:
            print(f"Uh-oh! Had a little hiccup decoding the JSON file at {file_path}. 😬")
            return None

