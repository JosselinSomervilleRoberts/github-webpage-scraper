import os
import time
import datetime

from deployment.server import JekyllServer
from fetcher.search import clone_repo, search_github_repos
from renderer.driver import save_random_screenshot, ScreenshotOptions


def main():
    path: str = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path, "repos")

    # Search for GitHub pages repositories
    repos = search_github_repos(
        created_after=datetime.datetime(2021, 1, 1),
        language="HTML",
        max_size_kb=1000,
        limits=50,
        verbose=True,
    )

    # Clone the repositories and start the Jekyll server
    for i, repo in enumerate(repos):
        print("\n" + "=" * 50)
        repo_name = f"{i}_{repo['name']}"
        clone_url = repo["clone_url"]
        port = 4000
        print(f"Cloning {clone_url} to {path}/{repo_name}")
        clone_repo(clone_url, path, repo_name)

        # Start the Jekyll server
        server = JekyllServer(f"{path}/{repo_name}", verbose=True)
        success: bool = server.start()

        if not success:
            print(f"Failed to start the server for {repo_name}. Skipping...")
            continue

        # Take a screenshot of a random page
        try:
            actions = save_random_screenshot(f"screenshot_{repo_name}.png", port=port)
        except Exception as e:
            print(f"Failed to take a screenshot: {e}")
            actions = []

        # Print the actions performed
        if actions:
            print(f"Actions performed to take the screenshot of {repo_name}:")
            for j, action in enumerate(actions):
                print(f"{j + 1}. {action}")

        # Stop the Jekyll server
        server.stop()

        # Delete the repository
        # print(f"Deleting {path}/{repo_name}")
        # os.system(f"rm -rf {path}/{repo_name}")


if __name__ == "__main__":
    main()
