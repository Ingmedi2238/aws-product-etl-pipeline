#!/usr/bin/env python3
"""
AWS Product ETL Pipeline Destroy Script
This script properly destroys all infrastructure including emptying S3 buckets
"""

import subprocess
import sys
import os
import shutil
import json

DEFAULT_AWS_PROFILE = "frank-aws-starter-profile"  # change this to your profile

def run_command(command):
    """Run a shell command and return result"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        print(f"Error: {result.stderr}")
        return None
    return result

def check_tools():
    """Check if required tools are installed"""
    if not shutil.which("terraform"):
        print("Error: Terraform not found")
        sys.exit(1)
    
    if not shutil.which("aws"):
        print("Error: AWS CLI not found")
        sys.exit(1)

def get_terraform_outputs():
    """Get terraform outputs to find bucket names"""
    print("Getting Terraform outputs...")
    result = run_command("terraform output -json")
    if result is None:
        print("Warning: Could not get Terraform outputs")
        return {}
    
    try:
        outputs = json.loads(result.stdout)
        return outputs
    except json.JSONDecodeError:
        print("Warning: Could not parse Terraform outputs")
        return {}

def empty_s3_bucket(bucket_name, profile):
    """Empty an S3 bucket of all objects and versions"""
    print(f"Emptying S3 bucket: {bucket_name}")
    
    # Delete all object versions
    print("Deleting all object versions...")
    result = run_command(f"aws s3api list-object-versions --bucket {bucket_name} --profile {profile}")
    if result and result.stdout.strip():
        try:
            versions = json.loads(result.stdout)
            
            # Delete object versions
            if 'Versions' in versions:
                for version in versions['Versions']:
                    key = version['Key']
                    version_id = version['VersionId']
                    print(f"Deleting version {version_id} of {key}")
                    run_command(f"aws s3api delete-object --bucket {bucket_name} --key \"{key}\" --version-id {version_id} --profile {profile}")
            
            # Delete delete markers
            if 'DeleteMarkers' in versions:
                for marker in versions['DeleteMarkers']:
                    key = marker['Key']
                    version_id = marker['VersionId']
                    print(f"Deleting delete marker {version_id} of {key}")
                    run_command(f"aws s3api delete-object --bucket {bucket_name} --key \"{key}\" --version-id {version_id} --profile {profile}")
        except json.JSONDecodeError:
            print("Warning: Could not parse object versions")
    
    # Force delete all objects (fallback)
    print("Force deleting all remaining objects...")
    run_command(f"aws s3 rm s3://{bucket_name} --recursive --profile {profile}")
    
    print(f"Bucket {bucket_name} emptied")

def cleanup_athena_workgroup(workgroup_name, profile):
    """Clean up Athena workgroup queries and named queries"""
    print(f"Cleaning up Athena workgroup: {workgroup_name}")
    
    # List and cancel any running queries
    print("Checking for running queries...")
    result = run_command(f"aws athena list-query-executions --work-group {workgroup_name} --profile {profile}")
    if result and result.stdout.strip():
        try:
            executions = json.loads(result.stdout)
            if 'QueryExecutionIds' in executions:
                for execution_id in executions['QueryExecutionIds'][:10]:  # Limit to recent queries
                    print(f"Stopping query execution: {execution_id}")
                    run_command(f"aws athena stop-query-execution --query-execution-id {execution_id} --profile {profile}")
        except json.JSONDecodeError:
            print("Warning: Could not parse query executions")
    
    # List and delete named queries
    print("Deleting named queries...")
    result = run_command(f"aws athena list-named-queries --profile {profile}")
    if result and result.stdout.strip():
        try:
            named_queries = json.loads(result.stdout)
            if 'NamedQueryIds' in named_queries:
                for query_id in named_queries['NamedQueryIds']:
                    print(f"Deleting named query: {query_id}")
                    run_command(f"aws athena delete-named-query --named-query-id {query_id} --profile {profile}")
        except json.JSONDecodeError:
            print("Warning: Could not parse named queries")
    
    print(f"Athena workgroup {workgroup_name} cleaned up")

def destroy_infrastructure():
    """Destroy all infrastructure with Terraform"""
    print("Destroying infrastructure with Terraform...")
    
    # First try to refresh and apply the updated configuration (with force_destroy)
    print("Refreshing Terraform configuration...")
    run_command("terraform init")
    run_command("terraform refresh")
    
    # Now destroy
    result = run_command("terraform destroy -auto-approve")
    if result is None:
        print("Failed to destroy infrastructure with Terraform.")
        print("You may need to manually delete some resources in AWS Console.")
        print("Common resources that might need manual deletion:")
        print("- Athena WorkGroup with query history")
        print("- S3 buckets with objects")
        sys.exit(1)
    print("Infrastructure destroyed")

def cleanup_terraform_files():
    """Clean up Terraform state and lock files"""
    print("Cleaning up Terraform files...")
    files_to_remove = [
        "terraform.tfstate",
        "terraform.tfstate.backup",
        ".terraform.lock.hcl",
        "output.json"
    ]
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Removed {file_name}")
    
    if os.path.exists(".terraform"):
        shutil.rmtree(".terraform")
        print("Removed .terraform directory")
    
    if os.path.exists("lambda/packages"):
        shutil.rmtree("lambda/packages")
        print("Removed lambda/packages directory")

def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--help":
        print("Usage: python destroy.py")
        print("This script will:")
        print("1. Get bucket names from Terraform outputs")
        print("2. Empty all S3 buckets")
        print("3. Destroy all infrastructure with Terraform")
        print("4. Clean up local Terraform files")
        sys.exit(0)
    
    print("AWS Product ETL Pipeline Destroy Script")
    print("WARNING: This will delete ALL infrastructure and data!")
    
    # Confirm destruction
    response = input("Are you sure you want to destroy everything? (type 'yes' to continue): ")
    if response.lower() != 'yes':
        print("Destruction cancelled")
        sys.exit(0)
    
    check_tools()
    
    # Get AWS profile from terraform.tfvars
    profile = DEFAULT_AWS_PROFILE # default
    if os.path.exists("terraform.tfvars"):
        with open("terraform.tfvars", 'r') as f:
            for line in f:
                if line.strip().startswith('aws_profile'):
                    profile = line.split('=')[1].strip().strip('"\'')
                    break
    
    print(f"Using AWS profile: {profile}")
    
    # Get bucket names from Terraform outputs
    outputs = get_terraform_outputs()
    
    # Empty S3 buckets if they exist
    buckets_cleaned = False
    
    if "s3_bucket_name" in outputs:
        bucket_name = outputs["s3_bucket_name"]["value"]
        empty_s3_bucket(bucket_name, profile)
        buckets_cleaned = True
    
    if "athena_results_bucket_name" in outputs:
        bucket_name = outputs["athena_results_bucket_name"]["value"]
        empty_s3_bucket(bucket_name, profile)
        buckets_cleaned = True
    
    # If we couldn't get outputs, try to find buckets by prefix
    if not buckets_cleaned:
        print("Terraform outputs not available. Searching for project buckets...")
        result = run_command(f"aws s3api list-buckets --profile {profile}")
        if result and result.stdout.strip():
            try:
                buckets_response = json.loads(result.stdout)
                for bucket in buckets_response.get('Buckets', []):
                    bucket_name = bucket['Name']
                    if 'shop-etl' in bucket_name:  # Match our project buckets
                        print(f"Found project bucket: {bucket_name}")
                        empty_s3_bucket(bucket_name, profile)
                        buckets_cleaned = True
            except json.JSONDecodeError:
                print("Warning: Could not parse S3 buckets list")
    
    if not buckets_cleaned:
        print("Warning: Could not find any project buckets to clean")
    
    # Clean up Athena workgroup
    if "athena_workgroup_name" in outputs:
        workgroup_name = outputs["athena_workgroup_name"]["value"]
        cleanup_athena_workgroup(workgroup_name, profile)
    else:
        print("Warning: Could not find Athena workgroup name in outputs")
    
    # Destroy infrastructure
    destroy_infrastructure()
    
    # Clean up local files
    cleanup_terraform_files()
    
    print("Complete cleanup finished!")
    print("All AWS resources have been destroyed and local files cleaned up.")

if __name__ == "__main__":
    main()