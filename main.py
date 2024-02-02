import requests
import os
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime

load_dotenv()

# Looks for token in .env file
headers = {
    "Authorization": os.getenv("GITHUB_TOKEN"),
    "Accept": "application/vnd.github+json",
}

# Search for repositories with 'github.io' in their name


def search_github_repos(
    created_after: datetime,
    language: Optional[str] = None,
    max_size_kb: int = 1000,
    limits: int = 100,
):
    query_parameters = {
        "size": f"<={max_size_kb}",
        "created": f">={created_after.strftime('%Y-%m-%d')}",
    }
    if language:
        query_parameters["language"] = language
    search_query = "github.io in:name "
    search_query += " ".join(
        [f"{key}:{value}" for key, value in query_parameters.items()]
    )
    url = (
        f"https://api.github.com/search/repositories?q={search_query}&per_page={limits}"
    )
    print("Searching for repositories with the following query:", url)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        print("Failed to retrieve data:", response.status_code)
        return []


def clone_repo(repo_url: str, download_path: str, repo_name: str):
    os.system(f"git clone {repo_url} {download_path}/{repo_name}")


def setup_gemfile(repo_path: str):
    # Check if Gemfile exists, if not, copy Gemfile.default to Gemfile
    if not os.path.exists(f"{repo_path}/Gemfile"):
        os.system(f"cp Gemfile.default {repo_path}/Gemfile")
        return

    # Gemfile exists, check if it has the jekyll gem
    if "jekyll" in open(f"{repo_path}/Gemfile").read():
        # TODO: figure out if we need to do anything here
        return

    # Gemfile exists, but doesn't have jekyll gem
    with open(f"{repo_path}/Gemfile", "a") as file:
        file.write('gem "jekyll", "~> 4.3.3"')


def serve_repo(repo_path: str):
    setup_gemfile(repo_path)
    os.system(f"cd {repo_path} && bundle install && bundle exec jekyll serve")


if __name__ == "__main__":
    print("Searching for repositories...")
    repos = search_github_repos(
        created_after=datetime(2024, 1, 1),
        language="HTML",
        max_size_kb=1000,
        limits=10,
    )
    print(f"Found {len(repos)} repositories\n")

    for i, repo in enumerate(repos):
        print(f"{i+1}. {repo['full_name']} - {repo['html_url']}")
        clone_repo(repo["clone_url"], "repos", f"{i}_{repo['name']}")
        serve_repo(f"repos/{i}_{repo['name']}")
