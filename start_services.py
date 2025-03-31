#!/usr/bin/env python3
"""
start_services.py

This script starts the Supabase stack first, waits for it to initialize, and then starts
the Local AI stack (OpenWebUI, LibreChat, MongoDB). Both stacks use the same Docker
Compose project name ("localai") so they appear together in Docker Desktop.
"""

import os
import subprocess
import shutil
import time

def run_command(cmd, cwd=None):
    """Run a shell command and print it."""
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)

def clone_supabase_repo():
    """Clone the Supabase repository using sparse checkout if not already present."""
    if not os.path.exists("supabase"):
        print("Cloning the Supabase repository...")
        run_command([
            "git", "clone", "--filter=blob:none", "--no-checkout",
            "https://github.com/supabase/supabase.git"
        ])
        os.chdir("supabase")
        run_command(["git", "sparse-checkout", "init", "--cone"])
        run_command(["git", "sparse-checkout", "set", "docker"])
        run_command(["git", "checkout", "master"])
        os.chdir("..")
    else:
        print("Supabase repository already exists, updating...")
        os.chdir("supabase")
        run_command(["git", "pull"])
        os.chdir("..")

def prepare_supabase_env():
    """Copy .env to .env in supabase/docker."""
    env_path = os.path.join("supabase", "docker", ".env")
    env_example_path = os.path.join(".env")
    print("Copying .env in root to .env in supabase/docker...")
    shutil.copyfile(env_example_path, env_path)

def stop_existing_containers():
    """Stop and remove existing containers for our unified project ('localai')."""
    print("Stopping and removing existing containers for the unified project 'localai'...")
    
    # Force remove any stuck containers first
    try:
        run_command(["docker", "rm", "-f", "mongodb", "open-webui"])
    except subprocess.CalledProcessError:
        # Ignore errors if containers don't exist
        pass
    
    run_command([
        "docker", "compose",
        "-p", "localai",
        "-f", "docker-compose.yml",
        "-f", "supabase/docker/docker-compose.yml",
        "down", "--remove-orphans"
    ])

def start_supabase():
    """Start the Supabase services (using its compose file)."""
    print("Starting Supabase services...")
    run_command([
        "docker", "compose", "-p", "localai", "-f", "supabase/docker/docker-compose.yml", "up", "-d"
    ])

def start_local_ai_stack():
    """Start the Local AI stack (OpenWebUI, LibreChat, MongoDB, etc.)."""
    print("Starting Local AI services (OpenWebUI, LibreChat, MongoDB)...")
    run_command([
        "docker", "compose", "-p", "localai", "-f", "docker-compose.yml", "up"
    ])

def main():
    stop_existing_containers()
    
    # Start Supabase
    # clone_supabase_repo()
    # prepare_supabase_env()
    # start_supabase()    
    # print("Waiting for Supabase to initialize...")
    # time.sleep(10)
    
    # Then start the Local AI stack
    start_local_ai_stack()

if __name__ == "__main__":
    main()
