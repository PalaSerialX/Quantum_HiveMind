from hive.utils.function_calls import *
from hive.utils.queen_brain import get_queen_bee_response
from hive.database.tiny_db import QueenBeeTaskManager
from hive.json_utils.json_handler import JsonConfigLoader
from json import JSONDecodeError

import queue
import time
import re
import json


class QueenBee:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.worker_bees = []
        self.task_manager = QueenBeeTaskManager()  # Initialize the task manager
        self.config_loader = JsonConfigLoader()  # Initialize the JsonConfigLoader
        self.system_messages = self.config_loader.system_messages
        self.system_prompts = self.config_loader.system_prompts
        self.function_metadata = self.config_loader.function_metadata

    def generate_unique_task_id(self, task_description, priority):
        # Take the first three words from the task description
        first_words = "_".join(task_description.split()[:3])

        # Add the priority
        combined = f"{first_words}_{priority}"

        # Add a timestamp for uniqueness
        unique_id = f"{combined}_{int(time.time())}"

        return unique_id

    def prepare_query_args(self, user_query: str):
        format_args = {
            'user_query': user_query,
            'function_metadata': self.function_metadata,
            # will Add more as I grow this
        }
        return format_args

    def assign_tasks(self):
        pending_tasks = self.task_manager.get_tasks_by_status("pending")
        if not pending_tasks:
            print("No pending tasks to assign. 🌼")
            return

    def receive_results(self, task_id, result):
        self.task_manager.update_task(task_id, {'status': 'completed', 'result': result})
        print(f"Task {task_id} has been completed! 🌟")

    def manage_hive(self):
        while not self.task_queue.empty():
            task = self.task_queue.get()
            # Here you can assign the task to a worker bee and get the result
            # For demonstration, let's assume the task is completed
            self.receive_results(task['_id'], "Task completed successfully")

    def decide_task_route(self, gpt4_content, user_query):
        decision = gpt4_content.strip()

        if decision == 'break_into_subtasks':
            return self.break_into_subtasks(user_query)
        elif decision == 'handle_it_myself':
            return self.execute_simple_task(user_query)
        elif decision == 'break_into_subtasks_and_clarify':
            return self.break_into_subtasks_and_clarify()
        else:
            return "Oops! I'm not sure what to do. 🤔"

    def execute_simple_task(self, user_query):
        # Prepare the arguments for the system prompt
        format_args = self.prepare_query_args(user_query)

        # Get the system message and prompt
        system_message, system_prompt = self.get_system_info(
            message_key='use_functions',
            prompt_key='Function_Selection_Prompt',
            format_args=format_args
        )

        # Replace the {user_query} placeholder in the system_message
        system_message = system_message.replace("{user_query}", user_query)

        # Query GPT-4 to decide which function to use
        queen_output = get_queen_bee_response(task=system_prompt, system_message=system_message)

        # Extract the content from the OpenAIObject
        queen_output = queen_output['choices'][0]['message']['content']

        # Extract just the JSON part from the gpt4_content
        json_match = re.search(r'\{.*\}', queen_output)
        if json_match:
            json_str = json_match.group(0)
            try:
                gpt4_content = json.loads(json_str)
            except JSONDecodeError:
                return f"Oops, couldn't decode the JSON 🌹"
        else:
            return f"Oops, couldn't find any JSON to decode 🌹"

        # Now gpt4_content should definitely be a dictionary
        if isinstance(gpt4_content, dict):
            # Parse and execute the function
            result, error = self.parse_and_execute_function(gpt4_content)

            if error:
                return f"Oops, something went wrong: {error} 🙁"
            else:
                return f"Here's what I found: {result} 🌟"
        else:
            return f"Oops, something's not right with the format 🌹"

    def break_into_subtasks(self, user_query):
        # Prepare the arguments for the system prompt
        format_args = self.prepare_query_args(user_query)

        # Modify the system prompt to include the user's query
        system_message, system_prompt = self.get_system_info(message_key='Task_Analysis')
        system_prompt = f"User Query: {user_query} {system_prompt}"

        # Query GPT-4 to decide which sub-tasks to create
        queen_output = get_queen_bee_response(task=system_prompt, system_message=system_message, max_tokens=2000)

        # Extract the content from the OpenAIObject
        queen_content = queen_output['choices'][0]['message']['content']

        json_content = json.loads(queen_content)

        if 'tasks' in json_content:
            sub_tasks = json_content['tasks']
        elif 'sub_tasks' in json_content:
            sub_tasks = json_content['sub_tasks']
        else:
            print("Neither 'tasks' nor 'sub_tasks' found. Initializing an empty list.")
            sub_tasks = []

        print(f"queen_content: {queen_content}")

        # Add these sub-tasks to your task manager with unique IDs
        for task in sub_tasks:
            unique_task_id = self.generate_unique_task_id(task['description'], task['priority'])
            category = task.get('category', None)  # Get the category if it exists, otherwise None
            self.task_manager.add_task(unique_task_id, task['description'], task['priority'], task['status'],
                                       category=category)

        # Now, let's assign those tasks!
        self.assign_tasks()

        return "Sub-tasks have been created, added, and assigned! 🌼🌟"

    def break_into_subtasks_and_clarify(self):
        # Code for asking for more info
        return "This Code Requires more Clarification"

    def get_system_info(self, message_key='Initial_Task_Input', prompt_key='Function_Selection_Prompt',
                        format_args=None):
        system_message = self.system_messages.get(message_key, "Default message")
        # Check if system_prompts has the key 'General_Prompts' or 'Specific_Prompts'
        if 'General_Prompts' in self.config_loader.system_prompts:
            self.system_prompts = self.config_loader.system_prompts['General_Prompts']
        else:
            print("Error: 'General_Prompts' key not found in system_prompts.")
            return "Error", "Error"

        # Now you can directly access it
        system_prompt = self.system_prompts.get(prompt_key, "Default prompt").format(
            **format_args) if format_args else "Default prompt"

        return system_message, system_prompt

    # In your parse_and_execute_function
    def parse_and_execute_function(self, parsed_output):
        try:
            function_name = parsed_output.get('function_name')
            args = parsed_output.get('args', {})

            # Execute the function
            shared_config = SharedConfig()
            func_dict = shared_config.get_func_dict()
            if function_name in func_dict:
                result = func_dict[function_name](**args)
                return result, None  # No error
            else:
                return None, "I couldn't find a function to handle your query. 😢"

        except Exception as e:
            return None, f"Oops! Something went wrong: {e} 😢"

    def process_user_query(self, user_query: str):
        format_args = self.prepare_query_args(user_query)
        system_message, prompt = self.get_system_info(format_args=format_args)

        # Replace the {user_query} placeholder in the system_message
        system_message = system_message.replace("{user_query}", user_query)

        # Query Queen
        query_response = get_queen_bee_response(task=prompt, system_message=system_message, model="gpt-3.5-turbo")

        # Extract the content from the Queen
        query_response = query_response['choices'][0]['message']['content']

        # Decide what to do next based on the result
        next_step = self.decide_task_route(query_response, user_query)
        return next_step


if __name__ == "__main__":
    # Create an instance of the QueenBee
    queen = QueenBee()

    # Start the hive management
    result = queen.process_user_query("I want you to figure out how to build a successful "
                                      "youtube channel, on deep pround level. ")

    # result = queen.assign_tasks()
    print(result)



