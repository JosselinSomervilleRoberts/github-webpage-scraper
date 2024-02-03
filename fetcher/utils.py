import os
from dotenv import load_dotenv
from typing import Dict


# Load the .env file
load_dotenv()


def get_headers() -> Dict[str, str]:
    """Get the headers for the GitHub API

    Returns:
        Dict[str, str]: The headers for the GitHub API
    """
    load_dotenv()
    return {
        "Authorization": os.getenv("GITHUB_TOKEN"),
        "Accept": "application/vnd.github+json",
    }
