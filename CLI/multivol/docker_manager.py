# docker_manager.py
# Docker resource management for MultiVolatility
# Handles container limits and system resource monitoring for multi-user scenarios

import docker
import os
import time
import threading
from collections import defaultdict

class DockerResourceManager:
    def __init__(self):
        self.client = docker.from_env()
        self.lock = threading.Lock()
        self.system_stats = {
            'max_concurrent_containers': self._calculate_max_containers(),
            'current_containers': 0,
            'container_by_scan': defaultdict(list)
        }
        
        # Start monitoring thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_system_resources, daemon=True)
        self.monitor_thread.start()
    
    def _calculate_max_containers(self):
        """Calculate maximum allowed concurrent containers based on system resources"""
        try:
            # Get system CPU and memory info
            cpu_count = os.cpu_count() or 4
            
            # Conservative approach: allow 2 containers per CPU core
            # Minimum of 4 containers, maximum of 16 to prevent system overload
            max_containers = max(4, min(16, cpu_count * 2))
            return max_containers
        except:
            return 8  # Default fallback
    
    def _monitor_system_resources(self):
        """Background thread to monitor system resources and adjust limits"""
        while self.monitoring_active:
            try:
                # Update container count
                containers = self.client.containers.list(all=True)
                running_containers = [c for c in containers if c.status == 'running']
                
                with self.lock:
                    self.system_stats['current_containers'] = len(running_containers)
            except:
                pass
            
            time.sleep(15)  # Update every 15 seconds
    
    def can_launch_containers(self, requested_count=1):
        """Check if system can handle requested number of new containers"""
        with self.lock:
            current = self.system_stats['current_containers']
            max_allowed = self.system_stats['max_concurrent_containers']
            
            return (current + requested_count) <= max_allowed
    
    def register_scan_containers(self, scan_id, container_names):
        """Register containers belonging to a specific scan"""
        with self.lock:
            self.system_stats['container_by_scan'][scan_id] = container_names
    
    def cleanup_scan_containers(self, scan_id):
        """Clean up containers for a completed scan"""
        with self.lock:
            if scan_id in self.system_stats['container_by_scan']:
                container_names = self.system_stats['container_by_scan'][scan_id]
                del self.system_stats['container_by_scan'][scan_id]
                
                # Try to remove containers
                for container_name in container_names:
                    try:
                        container = self.client.containers.get(container_name)
                        if container.status == 'exited':
                            container.remove()
                    except:
                        pass  # Container already removed or doesn't exist
    
    def get_system_status(self):
        """Get current system resource status"""
        with self.lock:
            return self.system_stats.copy()
    
    def shutdown(self):
        """Clean up and shutdown the resource manager"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

# Global instance for easy access
docker_manager = DockerResourceManager()

def get_docker_manager():
    """Get the global Docker resource manager instance"""
    return docker_manager