import queue

from hive.utils.function_calls import *
from hive.utils.queen_brain import get_queen_bee_response
from hive.database.tiny_db import QueenBeeTaskManager
from hive.json_utils.json_handler import JsonConfigLoader

import re
import json
from json import JSONDecodeError


class QueenBee:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.worker_bees = []
        self.task_manager = QueenBeeTaskManager()  # Initialize the task manager
        self.config_loader = JsonConfigLoader()  # Initialize the JsonConfigLoader
        self.system_messages = self.config_loader.system_messages
        self.system_prompts = self.config_loader.system_prompts
        self.function_metadata = self.config_loader.function_metadata

    def prepare_query_args(self, user_query: str):
        format_args = {
            'user_query': user_query,
            'function_metadata': self.function_metadata,
            # Add more as needed
        }
        return format_args

    def assign_tasks(self):
        pending_tasks = self.task_manager.get_tasks_by_status("pending")

        if not pending_tasks:
            print("No pending tasks to assign. 🌼")
            return

        system_message, _ = self.get_system_info(message_key='Sub_task')
        specific_prompts = self.config_loader.system_prompts['Specific_Prompts']

        user_query_prompt = specific_prompts['User_Query_Prompt']
        roadmap = specific_prompts['Roadmap']
        output_format = specific_prompts['Output_Format']

        # Take the first task for testing
        task = pending_tasks[0]

        format_args = {
            'user_query': task.get('description', 'No description'),
            'function_metadata': self.function_metadata,
            'roadmap': roadmap,
            'output_format': output_format
        }

        system_prompt = user_query_prompt.format(**format_args)
        system_prompt += f"\nRoadmap: {roadmap}\nOutput Format: {output_format}"

        print(f'this is the system_prompt: {system_prompt}')

        gpt4_output = get_queen_bee_response(task=system_prompt, system_message=system_message,
                                             max_tokens=2000, temperature=0.9)

        gpt4_content = gpt4_output['choices'][0]['message']['content']

        try:
            start_index = gpt4_content.index("{")
            end_index = gpt4_content.rindex("}") + 1
            json_str = gpt4_content[start_index:end_index]
            task_breakdown = json.loads(json_str)
        except (JSONDecodeError, ValueError):
            print(f"Oops! Invalid JSON format for task {task['_id']}. 🌹")
            return None  # Explicitly return None if JSON is invalid

        self.task_manager.update_task(task['_id'], {'breakdown': task_breakdown})
        self.task_queue.put(task)

        print(f"Task {task['_id']} has been assigned with a detailed breakdown! 🌼")

        return task_breakdown

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

        if decision == 'handle_it_myself':
            return self.execute_simple_task(user_query)
        elif decision == 'break_into_subtasks':
            return self.break_into_subtasks(user_query)
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
        gpt4_output = get_queen_bee_response(task=system_prompt, system_message=system_message)

        # Extract the content from the OpenAIObject
        gpt4_content = gpt4_output['choices'][0]['message']['content']

        # Extract just the JSON part from the gpt4_content
        json_match = re.search(r'\{.*\}', gpt4_content)
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
        gpt4_output = get_queen_bee_response(task=system_prompt, system_message=system_message, max_tokens=2000)

        # Extract the content from the OpenAIObject
        gpt4_content = gpt4_output['choices'][0]['message']['content']

        json_content = json.loads(gpt4_content)

        if 'tasks' in json_content:
            sub_tasks = json_content['tasks']
        elif 'sub_tasks' in json_content:
            sub_tasks = json_content['sub_tasks']
        else:
            print("Neither 'tasks' nor 'sub_tasks' found. Initializing an empty list.")
            sub_tasks = []

        print(f"gpt4_content: {gpt4_content}")

        # Add these sub-tasks to your task manager
        for task in sub_tasks:
            self.task_manager.add_task(task['_id'], task['description'], task['priority'], task['status'])

        print("Sub-tasks have been created and added to the task manager! 🌼")

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

        # Query GPT-4 (this is pseudo-code)
        gpt4_output = get_queen_bee_response(task=prompt, system_message=system_message)

        # Extract the content from the OpenAIObject
        gpt4_content = gpt4_output['choices'][0]['message']['content']

        # Decide what to do next based on the result
        next_step = self.decide_task_route(gpt4_content, user_query)
        return next_step


if __name__ == "__main__":
    # Create an instance of the QueenBee
    queen = QueenBee()

    # Start the hive management
    result = queen.process_user_query("What's the weather in new york?")

    # result = queen.assign_tasks()
    print(result)



