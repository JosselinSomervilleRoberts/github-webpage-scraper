import os
import time
import datetime
import cv2
import numpy as np
import argparse
from scipy import stats

from deployment.server import JekyllServer
from fetcher.search import clone_repo, search_github_repos
from fetcher.filter import filter_repo
from renderer.driver import save_random_screenshot, ScreenshotOptions


def percentage_of_most_frequent_color(image_path):
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        return "Image not found or path is incorrect"

    # Reshape the image to a 2D array where each row is a pixel
    pixels = img.reshape(-1, img.shape[2])

    # Find the most frequent color
    # Here we convert each pixel to a tuple to make them hashable, then use np.unique to find the most frequent one
    unique_colors, counts = np.unique(
        [tuple(row) for row in pixels], axis=0, return_counts=True
    )
    most_frequent_color = unique_colors[np.argmax(counts)]
    frequency_of_most_frequent = np.max(counts)

    # Calculate the total number of pixels
    total_pixels = img.shape[0] * img.shape[1]

    # Calculate the percentage of the most frequent color
    percentage = (frequency_of_most_frequent / total_pixels) * 100

    return percentage, most_frequent_color


def main(args):
    file_path: str = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(file_path, args.save_path)
    os.makedirs(path, exist_ok=True)
    os.makedirs(os.path.join(path, "repos"), exist_ok=True)
    os.makedirs(os.path.join(path, "images"), exist_ok=True)

    # Variables to store the results
    num_websites_collected: int = 0
    page: int = 0

    while num_websites_collected < args.num_websites_desired:
        page += 1
        print(f"Page {page} of the search results")

        # Search for GitHub pages repositories
        repos = search_github_repos(
            created_after=datetime.datetime.strptime(
                args.query_created_after, "%Y-%m-%d"
            ),
            language=args.query_language,
            max_size_kb=args.query_max_size_kb,
            limits=args.query_limits,
            page=page,
            verbose=True,
        )

        # Clone the repositories and start the Jekyll server
        for repo in enumerate(repos):
            print("\n" + "=" * 50)
            repo = repo[1]
            repo_name = (
                f"{num_websites_collected}_{repo['full_name'].replace('/', '_')}"
            )
            repo_path = os.path.join(path, "repos", repo_name)
            clone_url = repo["clone_url"]
            port = 4000
            print(f"Cloning {clone_url} to {repo_path}")
            clone_repo(clone_url, os.path.join(path, "repos"), repo_name)

            if not filter_repo(repo_path):
                print(f"{repo_name} does not meet the requirements. Skipping...")
                os.system(f"rm -rf {repo_path}")  # Delete the repository
                continue

            # Start the Jekyll server
            server = JekyllServer(repo_path, verbose=True)
            success: bool = server.start()

            if not success:
                print(f"Failed to start the server for {repo_name}. Skipping...")
                server.stop()
                os.system(f"rm -rf {repo_path}")
                continue

            # Take a screenshot of a random page
            image_path = os.path.join(path, "images", f"{repo_name}.png")
            try:
                scheenshot_options = ScreenshotOptions()
                scheenshot_options.num_actions_range = (0, args.max_num_actions)
                actions = save_random_screenshot(
                    image_path, port=port, options=scheenshot_options
                )
            except Exception as e:
                print(f"Failed to take a screenshot: {e}")
                server.stop()
                os.system(f"rm -rf {repo_path}")
                continue

            # Open the image and compute the amount of white pixels (percentage)
            white_pixels_ratio, _ = percentage_of_most_frequent_color(image_path)
            if white_pixels_ratio > args.max_white_percentage:
                print(
                    f"{repo_name} has too many white pixels ({white_pixels_ratio:.2f}%). Skipping..."
                )
                os.remove(image_path)  # Delete the screenshot
                server.stop()
                os.system(f"rm -rf {repo_path}")
                continue

            # Print the actions performed
            if actions:
                print(f"Actions performed to take the screenshot of {repo_name}:")
                for j, action in enumerate(actions):
                    print(f"{j + 1}. {action}")

            # Stop the Jekyll server
            server.stop()
            num_websites_collected += 1


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch and render GitHub pages")
    parser.add_argument(
        "--save_path",
        type=str,
        default="data",
        help="The path to save the repositories",
    )
    parser.add_argument(
        "--max_white_percentage",
        type=float,
        default=95.0,
        help="The maximum percentage of white pixels for a page to be considered a landing page",
    )
    parser.add_argument(
        "--max_num_actions",
        type=int,
        default=0,
        help="The maximum number of actions to take on a page",
    )
    parser.add_argument(
        "--query_language",
        type=str,
        default=None,
        help="The language to search for",
    )
    parser.add_argument(
        "--query_created_after",
        type=str,
        default="2024-01-01",
        help="The date to search for repositories created after",
    )
    parser.add_argument(
        "--query_max_size_kb",
        type=int,
        default=1000,
        help="The maximum size of the repository in KB",
    )
    parser.add_argument(
        "--query_limits",
        type=int,
        default=50,
        help="The maximum number of repositories to search for",
    )
    parser.add_argument(
        "--num_websites_desired",
        type=int,
        default=100,
        help="The number of websites to gather (after filtering)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
