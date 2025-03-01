import subprocess
import time
import os
from contextlib import contextmanager

from checks import (
    is_docker_running, is_sqheaven_running,
    check_sqheaven_status, DockerError, ContainerNotRunningError
)

# Default service name from docker-compose.yml
SERVICE_NAME = "db"

@contextmanager
def change_dir(path):
    """Context manager to change the current working directory."""
    original_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_path)

### 🏗️ Docker-Compose Control Functions ###
def build_image():
    """Build the SQHeaven Docker image using docker-compose."""
    print(f"🏗️ Building SQHeaven service using docker-compose...")
    with change_dir(".."):  # Ensure we return to the original directory
        try:
            subprocess.run(["docker-compose", "build"], check=True)
            print("✅ SQHeaven image built successfully.")
        except subprocess.CalledProcessError:
            raise DockerError("❌ Failed to build SQHeaven image.")
def run_compose_command(command):
    """Runs a docker-compose command from the correct directory."""
    compose_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Go up one level to `sqheaven`
    
    try:
        subprocess.run(command, cwd=compose_dir, check=True)
    except subprocess.CalledProcessError as e:
        raise DockerError(f"❌ Failed to run command: {command}\nError: {e}")
def start_sqheaven():
    """Start the SQHeaven container using docker-compose."""
    is_docker_running()

    if is_sqheaven_running():
        print("✅ SQHeaven database is already running.")
        return

    print("🚀 Starting SQHeaven database using docker-compose...")
    run_compose_command(["docker-compose", "up", "-d"])
    wait_for_postgres()
def stop_sqheaven():
    """Stop the SQHeaven container using docker-compose."""
    if not is_sqheaven_running():
        print("⚠️ SQHeaven database is not running.")
        return
    print("🛑 Stopping SQHeaven database using docker-compose...")
    try:
        subprocess.run(["docker-compose", "down"], check=True)
        print("✅ SQHeaven database stopped.")
    except subprocess.CalledProcessError:
        raise DockerError("❌ Failed to stop SQHeaven container.")

def wait_for_postgres():
    """Wait for PostgreSQL inside Docker to be ready."""
    print("⏳ Waiting for PostgreSQL to be ready...")
    for _ in range(20):  # Increase the wait time for robustness
        try:
            subprocess.run(["docker-compose", "exec", "-T", SERVICE_NAME, "pg_isready", "-U", "postgres"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print("✅ PostgreSQL is ready!")
            return
        except subprocess.CalledProcessError:
            time.sleep(1)
    raise DockerError("❌ PostgreSQL did not start in time.")

def run_in_sqheaven(command):
    """Execute an arbitrary command inside the running SQHeaven container."""
    if not is_sqheaven_running():
        raise ContainerNotRunningError("❌ SQHeaven container is not running.")
    try:
        result = subprocess.run(["docker-compose", "exec", "-T", SERVICE_NAME] + command.split(),
                                capture_output=True, text=True, check=True)
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return f"❌ Error executing command: {command}\n{e.stderr.strip()}"

def main():
    try:
        start_sqheaven()
        version = run_in_sqheaven("psql -U postgres -c 'SELECT version();'")
        print(f"🛠️ PostgreSQL Version:\n{version}")
    except DockerError as e:
        print(f"❌ Error: {e}")
    except ContainerNotRunningError as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            check_sqheaven_status()
        except ContainerNotRunningError as e:
            print(f"❌ Error: {e}")
        else:
            print("✅ All checks passed successfully.")

if __name__ == "__main__":
    main()
