from hive.utils.queen_brain import get_queen_bee_response


def summarization_bee(file_path, query=None):
    system_message = """Please summarize the text for me, and provide actionable insights or recommendations
                        based on those takeaways apply them to this Query: building and growing a youtube Channel """

    # Read the text from the file
    with open(file_path, 'r') as file:
        task_prompt = file.read()

    summary = get_queen_bee_response(task=task_prompt, system_message=system_message, max_tokens=2500,
                                     model="gpt-3.5-turbo-16k")

    summary_content = summary['choices'][0]['message']['content']
    print(summary_content)

    return summary_content


summarization_bee("D:/python/Quantum_HiveMind/sample_text.txt")
