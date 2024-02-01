import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Looks for token in .env file
headers = {
    "Authorization": os.getenv("GITHUB_TOKEN"),
    "Accept": "application/vnd.github+json",
}

# Search for repositories with 'github.io' in their name


def search_github_repos(max_size_kb: int, limits: int = 100):
    search_query = f"github.io in:name size:{max_size_kb}"
    url = (
        f"https://api.github.com/search/repositories?q={search_query}&per_page={limits}"
    )
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        print("Failed to retrieve data:", response.status_code)
        return []


repos = search_github_repos(10, limits=10)

for repo in repos:
    print(repo["full_name"], repo["html_url"])
