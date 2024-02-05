import subprocess
import os
import signal
from typing import Optional
import time
import socket


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

    def setup_config(self):
        # Check if _config.yml exists, if not, copy _config.default.yml to _config.yml
        if not os.path.exists(f"{self.repo_path}/_config.yml"):
            os.system(f"cp _config.default.yml {self.repo_path}/_config.yml")
            if self.verbose:
                print("Copied _config.default.yml to _config.yml")
            return

    def is_port_in_use(self, port):
        """Check if a port is in use on localhost."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    def kill_process_using_port(self, port):
        """Find and kill the process using the specified port."""
        command = f"lsof -ti:{port} | xargs kill -9"
        os.system(command)
        if self.verbose:
            print(f"Killed process using port {port}.")

    def start(self):
        """Start the Jekyll server in a separate process and monitor the output."""
        if self.is_port_in_use(self.port):
            if self.verbose:
                print(f"Port {self.port} is in use. Attempting to free it.")
            self.kill_process_using_port(self.port)

        self.setup_gemfile()
        self.setup_config()
        command_install = f"cd {self.repo_path} && bundle install"
        os.system(command_install)

        command_serve = (
            f"cd {self.repo_path} && bundle exec jekyll serve --port {self.port}"
        )
        self.process = subprocess.Popen(
            command_serve,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
            encoding="utf-8",  # This ensures stdout and stderr are strings
        )

        while True:
            # Stream the output
            output = self.process.stdout.readline()
            if output == "" and self.process.poll() is not None:
                break
            if output:
                print(output.strip())
                if "Server is running.. press ctrl-c to stop." in output.strip():
                    if self.verbose:
                        print(f"Jekyll server started at http://localhost:{self.port}")
                    break  # Server started successfully

            # Check stderr for any immediate errors
            error_output = self.process.stderr.readline()
            if error_output:
                pass
                print(f"Error: {error_output.strip()}")
                # # Here, you can parse the error and take action accordingly
                # break

    def stop(self, timeout=5):
        """Stop the Jekyll server and terminate the process with a timeout.

        Args:
            timeout (int, optional): Time to wait for the server to gracefully shut down. Defaults to 5 seconds.
        """
        if self.process:
            # Try to terminate the process group gracefully
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.terminate()

            # Wait for the process to end, checking periodically
            try:
                # Wait up to `timeout` seconds for process to terminate
                for _ in range(timeout):
                    if self.process.poll() is not None:  # Process has terminated
                        break
                    time.sleep(1)  # Wait a bit before checking again
                else:
                    # If the process is still alive after the timeout, kill it
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    self.process.kill()
                    self.process.wait()  # Wait for process to be killed
                    if self.verbose:
                        print("Jekyll server forcefully stopped.")
            except Exception as e:
                if self.verbose:
                    print(f"Error stopping the Jekyll server: {e}")

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
