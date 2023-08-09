import requests

def fetch_wikipedia_summary(search_query):
    search_url = "https://en.wikipedia.org/w/api.php"

    search_params = {
        'action': 'opensearch',
        'search': search_query,
        'limit': 1,
        'format': 'json'
    }

    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()
    
    if len(search_data) >= 2:
        search_results = search_data[1]
        if len(search_results) > 0:
            top_result = search_results[0]
            print(f'Top Result: {top_result}')

            page_url = search_data[3][0]
            print(f'URL: {page_url}')

            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{top_result}"
            summary_response = requests.get(summary_url)
            summary_data = summary_response.json()

            if 'extract' in summary_data:
                summary = summary_data['extract']
                #show more stuff as well
                print(f'Summary: {summary}')
            else:
                print('No summary found.')

        else:
            print('No related search result found.')
    else:
        print('No related search result found.')

# Example usage:
fetch_wikipedia_summary('YYZ airport')
