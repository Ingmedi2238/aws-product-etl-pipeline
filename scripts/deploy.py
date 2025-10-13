#!/usr/bin/env python3
"""
Simple AWS Product ETL Pipeline Deployment Script
"""

import subprocess
import sys
import os
import shutil

def run_command(command):
    """Run a shell command"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        sys.exit(1)
    return result

def check_tools():
    """Check if required tools are installed"""
    if not shutil.which("terraform"):
        print("Error: Terraform not found")
        sys.exit(1)
    
    if not shutil.which("aws"):
        print("Error: AWS CLI not found")
        sys.exit(1)

def create_tfvars():
    """Create terraform.tfvars if it doesn't exist"""
    if not os.path.exists("terraform.tfvars"):
        if os.path.exists("terraform.tfvars.example"):
            shutil.copy("terraform.tfvars.example", "terraform.tfvars")
            print("Created terraform.tfvars from example")
        else:
            print("Warning: terraform.tfvars.example not found")

def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy.py [init|plan|apply|output]")
        print("For destroying resources, use: python scripts/destroy.py")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    print("AWS Product ETL Pipeline Deployment")
    print(f"Action: {action}")
    
    check_tools()
    create_tfvars()
    
    if action == "init":
        run_command("terraform init")
    
    elif action == "plan":
        run_command("terraform init")
        run_command("terraform plan")
    
    elif action == "apply":
        run_command("terraform init")
        run_command("terraform apply")
    
    elif action == "output":
        run_command("terraform output")
    
    elif action == "destroy":
        print("For destroying resources, use the dedicated destroy script:")
        print("python scripts/destroy.py")
        print("This ensures proper S3 bucket cleanup before destruction.")
        sys.exit(1)
    
    else:
        print("Invalid action. Use: init, plan, apply, or output")
        print("For destroying resources, use: python scripts/destroy.py")
        sys.exit(1)
    
    print("Done")

if __name__ == "__main__":
    main()