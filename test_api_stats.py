#!/usr/bin/env python3

# Test simple pour vérifier ce que renvoie l'API /stats
# Sans dépendre de Docker

import json

# Simuler ce que fait la fonction get_stats() dans api.py
def simulate_get_stats():
    # Valeurs par défaut
    docker_stats = {
        "max_concurrent_containers": 8,
        "current_containers": 0,
        "system_load": "unknown"
    }
    
    # Simuler l'échec de docker_manager
    try:
        # Cela va échouer car docker n'est pas disponible
        from docker_manager import get_docker_manager
        docker_mgr = get_docker_manager()
        docker_stats = docker_mgr.get_system_status()
        docker_stats['system_load'] = "normal" if docker_stats['current_containers'] < docker_stats['max_concurrent_containers'] * 0.8 else "high"
    except Exception as e:
        print(f"[WARNING] Failed to get Docker stats: {e}")
        # On garde les valeurs par défaut
    
    return {
        "total_cases": 0,
        "processing": 0,
        "total_evidences": 0,
        "total_symbols": 0,
        "docker_stats": docker_stats
    }

if __name__ == "__main__":
    result = simulate_get_stats()
    print("Simulated API /stats response:")
    print(json.dumps(result, indent=2))
    print(f"\nDocker stats max_concurrent_containers: {result['docker_stats'].get('max_concurrent_containers', 'NOT FOUND')}")
