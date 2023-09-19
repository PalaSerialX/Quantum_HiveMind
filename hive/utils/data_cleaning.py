# Read the search_results.txt file with UTF-8 encoding
with open('D:/python/Quantum_HiveMind/hive/search_results/search_results.txt', 'r', encoding='utf-8') as file:
    raw_data = file.readlines()


# Function to clean search results
def clean_search_results(search_results):
    cleaned_results = []

    for result in search_results:
        # Evaluate the string as a dictionary
        result_dict = eval(result)

        cleaned_result = {
            'title': result_dict.get('title', 'N/A'),
            'url': result_dict.get('href', 'N/A'),
            'summary': result_dict.get('body', 'N/A')
        }
        cleaned_results.append(cleaned_result)
    return cleaned_results


