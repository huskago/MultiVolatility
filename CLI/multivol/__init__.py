# MultiVolatility package
# This file can be used to import key components

try:
    from .docker_manager import DockerResourceManager, get_docker_manager
except ImportError:
    pass  # Optional dependency for resource management