import requests
from typing import Optional, Any, Dict, List
from datetime import datetime
import os

from .utils import get_headers


def search_github_repos(
    created_after: datetime,
    language: Optional[str] = None,
    max_size_kb: int = 1000,
    limits: int = 100,
    verbose: bool = False,
) -> List[Dict[str, Any]]:
    """Search for GitHub pages repositories

    Args:
        created_after (datetime): The date to search from
        language (Optional[str], optional): The language to search for. Defaults to None.
        max_size_kb (int, optional): The maximum size of the repository in KB. Defaults to 1000.
        limits (int, optional): The maximum number of repositories to retrieve. Defaults to 100.
        verbose (bool, optional): Whether to print the search query. Defaults to False.

    Returns:
        List[Dict[str, Any]]: A list of repositories that match the search criteria

    Raises:
        Exception: If the request fails
    """
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
    if verbose:
        print("Searching for repositories with the following query:", url)
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()["items"]
    else:
        raise Exception(f"Failed to retrieve data: {response.status_code}")


def clone_repo(repo_url: str, download_path: str, repo_name: str):
    """Clone a repository from GitHub

    Args:
        repo_url (str): The URL of the repository
        download_path (str): The path to download the repository to
        repo_name (str): The name of the repository
    """
    os.system(f"git clone {repo_url} {download_path}/{repo_name}")


if __name__ == "__main__":
    # Example usage
    repos = search_github_repos(
        datetime(2021, 1, 1), language="JavaScript", verbose=True, limits=10
    )
    for i, repo in enumerate(repos):
        print(f"{i+1}. {repo['full_name']}: {repo['clone_url']}")
