import subprocess

class DockerError(Exception):
    """Base exception for Docker-related issues."""
    pass

class DockerNotRunningError(DockerError):
    """Raised when Docker is not running."""
    pass

class ContainerNotRunningError(DockerError):
    """Raised when the SQHeaven container is not running."""
    pass

class UnexpectedImageError(DockerError):
    """Raised when the SQHeaven container is using an unexpected image."""
    def __init__(self, image_name):
        super().__init__(f"Unexpected SQHeaven image detected: {image_name}")
        self.image_name = image_name

# Define allowed SQHeaven images
ALLOWED_IMAGE_NAMES = {
    "sqheaven-pg:latest",
    "sqheaven-pg:dev",
    "sqheaven-pg:custom"
}

CONTAINER_NAME = "sqheaven-postgres"
DOCKER_IMAGE = "sqheaven-pg:latest"

### 🚀 Docker Status Check Functions ###
def is_docker_running():
    """Check if Docker is installed and running."""
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        raise DockerNotRunningError("Docker is not running or unavailable.")

def is_image_built():
    """Check if the SQHeaven image is built."""
    try:
        subprocess.run(["docker", "image", "inspect", DOCKER_IMAGE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def is_sqheaven_running():
    """Check if the SQHeaven container is running."""
    try:
        output = subprocess.run(["docker", "ps", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Image}}"],
                                capture_output=True, text=True, check=True)
        if not output.stdout.strip():
            return False  # Container not running
        return True
    except subprocess.CalledProcessError:
        return False

def is_proper_sqheaven_running():
    """Ensure the running sqheaven-postgres container is using an allowed image name."""
    try:
        output = subprocess.run(["docker", "ps", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Image}}"],
                                capture_output=True, text=True, check=True)
        image_name = output.stdout.strip()

        if image_name not in ALLOWED_IMAGE_NAMES:
            raise UnexpectedImageError(image_name)

        return True
    except subprocess.CalledProcessError:
        return False

def check_sqheaven_status():
    """Runs all checks and raises appropriate exceptions if a check fails."""
    is_docker_running()
    if not is_sqheaven_running():
        raise ContainerNotRunningError("SQHeaven container is not running.")
    
    is_proper_sqheaven_running()
    return True
