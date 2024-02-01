import requests

# Replace 'your_token_here' with your GitHub personal access token
headers = {
    "Authorization": "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",
    "Accept": "application/vnd.github+json",
}

# Search for repositories with 'github.io' in their name
search_query = "github.io in:name"


def search_github_repos(query: str, limits: int = 100):
    url = f"https://api.github.com/search/repositories?q={query}&per_page=100"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        print("Failed to retrieve data:", response.status_code)
        return []


repos = search_github_repos(search_query)

for repo in repos:
    print(repo["full_name"], repo["html_url"])
