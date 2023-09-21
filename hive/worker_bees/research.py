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
task_manager = QueenBeeTaskManager()

# Create a new dictionary to store unique cherries
cherry_dict = {}


def parse_extracted_keywords(keywords_str):
    # Use regular expressions to find text that comes after numbers and a dot
    queries = re.findall(r'\d+\.\s*(.*)', keywords_str)

    # Remove extra quotes if any
    cleaned_queries = [query.strip('"') for query in queries]
    return cleaned_queries


def query_keywords():
    task_keyword_dict = {}
    pending_research_tasks = task_manager.get_tasks_by_status_and_type("Pending", "Research")

    for task in pending_research_tasks:
        parent_task_id = task.get('_id', '')
        description = task.get('description', '')

        system_message = "Please analyze this task and provide 5 queries " \
                         "to be used for search results list them by new lines."

        # Analyze the task description to generate keywords or queries
        analyzed_data = get_queen_bee_response(task=description, system_message=system_message,
                                               max_tokens=200, model="gpt-3.5-turbo")

        extracted_keywords = analyzed_data.get('choices', [{}])[0].get('message', {}).get('content', '')

        # Parse the extracted keywords
        parsed_keywords = parse_extracted_keywords(extracted_keywords)

        print(f"Parent Task ID: {parent_task_id}")  # For debugging
        print(f"Description: {description}")  # For debugging
        print(f"Parsed Keywords: {parsed_keywords}")  # For debugging

        # Store the parsed keywords and description against the Parent Task ID
        task_keyword_dict[parent_task_id] = {'keywords': parsed_keywords, 'description': description}

    return task_keyword_dict


def collect_data():
    task_keyword_dict = query_keywords()

    seen_urls = set()
    batch = []

    for parent_task_id, task_info in task_keyword_dict.items():
        keywords = task_info['keywords']
        description = task_info['description']

        print(f"Working on task: {parent_task_id}")

        for search in keywords:
            ddg_data = search_ddg(search)
            time.sleep(2)

            ddg_data_str = [str(item) for item in ddg_data]
            clean_results = clean_search_results(ddg_data_str)

            for result in clean_results:
                title = result.get('title', 'N/A')
                url = result.get('url', 'N/A')

                # Skip YouTube URLs
                if 'youtube.com' in url:
                    continue

                db.insert_cherry(title=title, url=url, keywords=keywords,
                                 status="Active", unique_task_id=parent_task_id)

                if url not in seen_urls and len(batch) < 100:
                    seen_urls.add(url)
                    batch.append({'title': title, 'url': url})

        system_message = f"""Search Query: {description}\nInstruction: Please look through 
                         the titles that were searched and pick the top cherries!
                         output between 8 and 15 titles on new line that closest matches the query"""

        task_prompt = "\n".join([f"{item.get('title', '')} {item.get('url', '')}" for item in batch])

        analyzed_data = get_queen_bee_response(task=task_prompt, system_message=system_message, max_tokens=2500,
                                               model="gpt-3.5-turbo-16k")
        # reset batch list
        batch = []

        content = analyzed_data.get('choices', [{}])[0].get('message', {}).get('content', '')

        cherry_titles = content.split('\n')

        for title in cherry_titles:
            main_title = re.sub(r'^\d+\.\s*', '', title).replace('"', '').replace("'", '').lstrip('- ').split(' - ')[
                0].strip()

            if not main_title:
                print("Skipping empty title")
                continue

            matching_records = db.fetch_cherries_by_partial_title(main_title)

            if matching_records:
                record = matching_records[0]
                exact_title_from_db = record[2]

                db.update_cherry_status_by_title(title=exact_title_from_db, is_cherry=True, status="Active")
            else:
                print(f"Skipping title not found in database: {main_title}")

        # remove duplicates and non-cherries keep db tidy
        db.clean_up_database()
        print("All research tasks have been completed! 🌼")


# Call the function to start collecting data
collect_data()
