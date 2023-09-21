from hive.utils.queen_brain import get_queen_bee_response
from hive.database.postgres_sql import ChatContextManager

# Initialize ChatContextManager
chat_manager = ChatContextManager()


def chat(user_id, user_input, system_message="You are a helpful assistant."):
    print(f'this is the user input: {user_input}')

    # Save the new user input to the database
    chat_manager.save_chat_history(user_id, "user", user_input)

    # Fetch the updated chat history
    context = chat_manager.fetch_chat_history(user_id)

    # Generate the new response
    queen_output = get_queen_bee_response(task=user_input, system_message=system_message,
                                          max_tokens=2000, chat_history=context, user_id=user_id, verbose=True)
    # parse queen_output to get the actual message text
    queen_message_content = queen_output['choices'][0]['message']['content']

    # Save the new messages directly to the database
    chat_manager.save_chat_history(user_id, "assistant", queen_message_content)

    return queen_message_content


chat("awesome_one", "so tell me about their whiskers")
