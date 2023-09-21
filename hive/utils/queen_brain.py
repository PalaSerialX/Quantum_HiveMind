from hive.database.postgres_sql import ChatContextManager

from dotenv import load_dotenv
import os
import openai

# Load the environment variables
load_dotenv()

# Set up OpenAI API credentials
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize ChatContextManager
chat_manager = ChatContextManager()


def get_queen_bee_response(task, system_message="You are a helpful assistant.",
                           verbose=False, max_tokens=150, temperature=0.6,
                           model="gpt-4-0613", chat_history=None, user_id=None):
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

    if chat_history:
        formatted_messages = [{"role": "system", "content": system_message}]

        for message in chat_history:
            role = "user" if message[2] == 'user' else "assistant"
            formatted_messages.append({"role": role, "content": message[3]})
    else:
        formatted_messages = [
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
        messages=formatted_messages
    )

    # Extract the actual text from the response object
    response_text = response['choices'][0]['message']['content']

    if verbose:
        # Fetch the latest chat history
        context = chat_manager.fetch_chat_history(user_id)
        context.append((None, user_id, 'assistant', response_text, None))
        print("Verbose Mode: Chat Context:")
        for idx, message in enumerate(context):
            role = "Queen Bee" if message[2] == 'assistant' else "User"
            print(f"{role}: {message[3]}")
        print("End of Chat Context")

    # Debugging to see the Responses we get back from GPT
    print(response)

    return response




