from dotenv import load_dotenv
import os
import openai

# Load the environment variables
load_dotenv()

# Set up OpenAI API credentials
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_queen_bee_response(task, system_message="You are a helpful assistant.",
                           verbose=False, max_tokens=150, temperature=0.6, model="gpt-4-0613"):
    """
        This function generates a response from the Queen Bee (GPT-4 model) to a given task.

        Parameters:
        task (str): The task that the Queen Bee needs to respond to.
        system_message (str, optional): A system message that sets the behavior of the Queen Bee.
        Defaults to "You are a helpful assistant.".
        verbose (bool, optional): If True, the task being sent to the AI is printed. Defaults to False.

        Returns:
        str: The response from the Queen Bee to the task.
        """
    # If verbose is True, print the task
    if verbose:
        print("Task being sent to the AI:")
        print(f"Task: {task}")

    # Format the task for the AI
    formatted_task = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": task}
    ]

    max_tokens = max_tokens
    temperature = temperature
    model = model

    # Generate the response using GPT-4
    response = openai.ChatCompletion.create(
        temperature=temperature,  # Adjust this value to change the randomness of the output
        max_tokens=max_tokens,  # Adjust this value to change the maximum length of the output
        model=model,  # Use GPT-4 model
        messages=formatted_task,

    )

    print(response)
    return response


# get_queen_bee_response('Hi')


