import os
import time
import datetime
import cv2
import numpy as np

from deployment.server import JekyllServer
from fetcher.search import clone_repo, search_github_repos
from fetcher.filter import filter_repo
from renderer.driver import save_random_screenshot, ScreenshotOptions


def compute_percentage_of_white_pixels(image_path: str, tolerance: int = 10) -> float:
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        return "Image not found or path is incorrect"

    # Define the lower bound for white considering the tolerance
    lower_bound = 255 - tolerance

    # Count pixels within the tolerance for being considered white
    # This creates a mask where all "white" pixels according to our tolerance are True
    white_pixels_mask = np.all(img >= [lower_bound, lower_bound, lower_bound], axis=-1)

    # Count the number of True values in our mask
    white_pixels = np.sum(white_pixels_mask)

    # Calculate total pixels
    total_pixels = (
        img.shape[0] * img.shape[1]
    )  # img.shape gives the dimensions of the image (height, width, channels)

    # Calculate percentage
    percentage = (white_pixels / total_pixels) * 100

    return percentage


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
        repo_path = os.path.join(path, repo_name)
        clone_url = repo["clone_url"]
        port = 4000
        print(f"Cloning {clone_url} to {repo_path}")
        clone_repo(clone_url, path, repo_name)

        if not filter_repo(repo_path):
            print(f"{repo_name} does not meet the requirements. Skipping...")
            continue

        # Start the Jekyll server
        server = JekyllServer(f"{path}/{repo_name}", verbose=True)
        success: bool = server.start()

        if not success:
            print(f"Failed to start the server for {repo_name}. Skipping...")
            continue

        # Take a screenshot of a random page
        image_path = f"screenshot_{repo_name}.png"
        try:
            actions = save_random_screenshot(image_path, port=port)
        except Exception as e:
            print(f"Failed to take a screenshot: {e}")
            continue

        # Open the image and compute the amount of white pixels (percentage)
        white_pixels_ratio: float = compute_percentage_of_white_pixels(image_path)
        print(f"Percentage of white pixels: {white_pixels_ratio:.2f}%")

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
