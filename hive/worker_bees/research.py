from hive.utils.queen_brain import get_queen_bee_response
from hive.database.tiny_db import QueenBeeTaskManager
from hive.utils.function_calls import search_ddg
from hive.utils.data_cleaning import clean_search_results
from hive.database.postgres_sql import CherryDatabase

import time
import tiktoken
import re


# Initialize the encoding for GPT-3.5-turbo
enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Initialize database connection (assuming you've already set up the db object)
db = CherryDatabase()


def collect_data():
    # Initialize title_url_dict to store titles and URLs
    title_url_dict = {}

    task_manager = QueenBeeTaskManager()
    pending_research_tasks = task_manager.get_tasks_by_status_and_type("pending", "Research")

    for task in pending_research_tasks:
        parent_task_id = task.get('_id', '')
        query = task['breakdown'].get('ImmediateNextSteps', [])
        keywords = task.get('breakdown', {}).get('QuerySources', {}).get('keywords', []) if 'QuerySources' in task.get(
            'breakdown', {}) else []

        print(f"Working on task: {task}")

        seen_urls = set()
        batch = []
        batches = []
        current_token_count = 0

        for search in keywords:
            ddg_data = search_ddg(search)
            time.sleep(2)

            # Convert each dictionary in the list to a string
            ddg_data_str = [str(item) for item in ddg_data]

            clean_results = clean_search_results(ddg_data_str)

            for result in clean_results:
                title = result.get('title', 'N/A')
                url = result.get('url', 'N/A')
                title_url_dict[title] = url

                # Insert the cleaned result into the database
                db.insert_cherry(title=title, url=url, keywords=keywords, status="Active")

                if url not in seen_urls:
                    seen_urls.add(url)
                    title_url_dict[title] = url

                    message_tokens = list(enc.encode(title + " " + url))
                    new_token_count = len(message_tokens)

                    if current_token_count + new_token_count > 8000:
                        batches.append(batch)
                        batch = []
                        current_token_count = 0

                    batch.append({'title': title, 'url': url})
                    current_token_count += new_token_count

        if batch:
            batches.append(batch)

        system_message = f"Query: {query}\nInstruction: Please look through the search results and pick the top cherries!"

        for batch in batches:
            task_prompt = "\n".join([f"{item.get('title', '')} {item.get('url', '')}" for item in batch])

            analyzed_data = get_queen_bee_response(task=task_prompt, system_message=system_message,
                                                   max_tokens=2500, model="gpt-3.5-turbo-16k")

            content = analyzed_data.get('choices', [{}])[0].get('message', {}).get('content', '')

            cherry_titles = content.split('\n')

            # Loop through the cherry titles
            for title in cherry_titles:
                title = title.strip()
                # Remove numbers and dots at the beginning of the title
                title = re.sub(r'^\d+\.\s*', '', title)

                # Remove quotes from the title
                title = title.replace('"', '').replace("'", "")

                # Split the title at the first dash or hyphen
                main_title = title.split(' - ')[0]

                if not main_title:
                    print("Skipping empty title")
                    continue

                # Fetch matching records from the database using partial matching
                matching_records = db.fetch_cherries_by_partial_title(main_title)

                if matching_records:
                    record = matching_records[0]
                    url = record[3]
                    print(f"Found matching cherry with title: {main_title}, url: {url}")

                    # Update the cherry status in the database
                    db.update_cherry_status(title=main_title, url=url, status="Active", is_cherry=True,
                                            unique_task_id=parent_task_id)

                else:
                    print(f"Skipping title not found in database: {main_title}")

    print("All research tasks have been completed! 🌼")


# # Call the function to start collecting data
collect_data()




