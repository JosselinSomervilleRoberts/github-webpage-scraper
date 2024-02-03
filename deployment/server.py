import subprocess
import os
import signal
from typing import Optional


class JekyllServer:
    def __init__(self, repo_path: str, verbose: bool = False, port: int = 4000):
        self.repo_path: str = repo_path
        self.verbose: bool = verbose
        self.port: int = port
        self.process: Optional[subprocess.Popen] = None

    def setup_gemfile(self):
        # Check if Gemfile exists, if not, copy Gemfile.default to Gemfile
        if not os.path.exists(f"{self.repo_path}/Gemfile"):
            os.system(f"cp Gemfile.default {self.repo_path}/Gemfile")
            if self.verbose:
                print("Copied Gemfile.default to Gemfile")
            return

        # Gemfile exists, check if it has the jekyll gem
        if "jekyll" in open(f"{self.repo_path}/Gemfile").read():
            # TODO: figure out if we need to do anything here
            return

        # Gemfile exists, but doesn't have jekyll gem
        with open(f"{self.repo_path}/Gemfile", "a") as file:
            file.write('gem "jekyll", "~> 4.3.3"')
            if self.verbose:
                print("Added jekyll gem to Gemfile")

    def start(self):
        """Start the Jekyll server in a separate process."""
        self.setup_gemfile()
        command = f"cd {self.repo_path} && bundle install && bundle exec jekyll serve --port {self.port}"
        self.process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
        )
        if self.verbose:
            print("Jekyll server started.")

    def stop(self):
        """Stop the Jekyll server and terminate the process."""
        if self.process:
            os.killpg(
                os.getpgid(self.process.pid), signal.SIGTERM
            )  # Send SIGTERM to the process group
            self.process.terminate()
            self.process = None
            if self.verbose:
                print("Jekyll server stopped.")
        elif self.verbose:
            print("Jekyll server is not running.")


def main(path: str, repo_name: str):
    from fetcher.search import clone_repo
    import time

    clone_url: str = "https://github.com/clickerultimate/clickerultimate.github.io.git"
    delay_alive: int = 30

    # Clone the repository
    print(f"Cloning {clone_url} to {path}/{repo_name}")
    clone_repo(clone_url, path, repo_name)

    # Start the Jekyll server
    server = JekyllServer(f"{path}/{repo_name}", verbose=True)
    server.start()
    print(f"Jekyll server started at http://localhost:{server.port}")

    # Stop the Jekyll server after delay_alive seconds
    print(f"Keeping the server alive for {delay_alive} seconds...")
    time.sleep(delay_alive)
    server.stop()

    # Delete the repository
    print(f"Deleting {path}/{repo_name}")
    os.system(f"rm -rf {path}/{repo_name}")
    print("Repository deleted.")


if __name__ == "__main__":
    path: str = os.path.dirname(os.path.realpath(__file__))
    repo_name: str = "repo_demo"

    try:
        main(path, repo_name)
    except KeyboardInterrupt:
        print("Interrupted by the user.")
        answer = None
        while answer not in ("y", "n"):
            answer = input("Do you want to delete the repository? (y/n): ").lower()
        if answer == "y":
            os.system(f"rm -rf {path}/{repo_name}")
            print("Repository deleted.")
        else:
            print("Repository not deleted.")
    except Exception as e:
        print(f"An error occurred: {e}")
        os.system(f"rm -rf {path}/{repo_name}")
        print("Repository deleted.")
