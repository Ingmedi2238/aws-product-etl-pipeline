# AWS Product ETL Pipeline

A comprehensive data engineering pipeline built with Terraform that extracts product data from DummyJSON API, 
processes it with AWS Lambda, stores it in S3, and makes it queryable through AWS Glue and Amazon Athena.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DummyJSON     │    │   AWS Lambda    │    │      S3         │
│      API        │───▶│   ETL Function  │───▶│    Bucket       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐             │
│   Amazon        │◀───│   AWS Glue      │◀────────────┘
│    Athena       │    │   Crawler       │
└─────────────────┘    └─────────────────┘
```

## Features

- **Automated ETL Pipeline**: Extracts 30+ products from DummyJSON API with business transformations
- **Data Cataloging**: AWS Glue automatically discovers and catalogs data schema
- **Serverless Analytics**: Query data directly from S3 using Amazon Athena
- **Infrastructure as Code**: Complete infrastructure provisioned with Terraform
- **Modular Architecture**: Reusable Terraform modules for easy maintenance
- **Security Best Practices**: Least privilege IAM roles and secure resource access
- **Random Naming**: Unique resource names to avoid conflicts

## Project Structure

```
aws-product-etl-pipeline/
├── README.md                   # This file
├── main.tf                     # Root Terraform configuration
├── variables.tf                # Input variables
├── outputs.tf                  # Output values
├── terraform.tfvars.example    # Example variable values
├── versions.tf                 # Provider requirements
├── .gitignore                  # Git ignore rules
├── 
├── modules/                    # Terraform modules
│   ├── s3/                     # S3 buckets
│   ├── iam/                    # IAM roles and policies
│   ├── lambda/                 # Lambda function
│   ├── glue/                   # AWS Glue components
│   └── athena/                 # Amazon Athena workgroup
├── 
├── lambda/
│   └── etl_function/
│       ├── lambda_function.py  # Main ETL logic
│       ├── config.py          # Configuration settings
│       └── requirements.txt    # Python dependencies
├── 
└── scripts/
    ├── deploy.py              # Deployment script
    └── destroy.py             # Cleanup script
```

## Prerequisites

- **AWS CLI** configured with appropriate credentials
- **Terraform** >= 1.0
- **Python** 3.11+
- **PowerShell** (for Windows users)

## Quick Start Guide

### Step 1: Set Up AWS Profile

If you don't have AWS CLI configured, set it up:

```bash
# Install AWS CLI (if not already installed)
# Windows: Download from AWS website
# macOS: brew install awscli
# Linux: sudo apt install awscli

# Configure your AWS credentials
aws configure --profile your-profile-name
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key 
- Default region (e.g., `eu-west-1`)
- Default output format: `json`

Verify your setup:
```bash
aws sts get-caller-identity --profile your-profile-name
```

### Step 2: Clone and Configure

```bash
# Clone the repository 
git clone <url-here>

# after
cd aws-product-etl-pipeline

# Copy and edit configuration
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your settings:
```hcl
# Project Configuration
project_name = "shop-etl"
environment  = "dev"

# AWS Configuration  
aws_region  = "eu-west-1"              # Your preferred region
aws_profile = "your-profile-name"      # Your AWS CLI profile

# S3 Configuration (this will have random suffix added)
s3_bucket_name         = "shop-etl-de-101"
athena_results_bucket  = "shop-etl-athena-results"

# Lambda Configuration
lambda_memory_size = 512
lambda_timeout     = 300

# Glue Configuration
glue_database_name = "shop_products_db"
glue_crawler_name  = "shop-products-crawler"

# Athena Configuration
athena_workgroup_name = "shop-etl-workgroup"
```

### Step 3: Deploy Infrastructure

```bash
# Deploy using the deployment script
python scripts/deploy.py apply
```

This will:
1. Initialize Terraform
2. Create 18 AWS resources:
   - 2 S3 buckets (with random suffixes)
   - Lambda function with ETL code
   - IAM roles and policies
   - Glue database and crawler
   - Athena workgroup
   - CloudWatch log group

**Expected Output:**
```
Apply complete! Resources: 18 added, 0 changed, 0 destroyed.

Outputs:
s3_bucket_name = "shop-etl-de-101-<with-some-prefix>"
lambda_function_name = "shop-etl-etl-function"
...
```

### Step 4: Test the ETL Pipeline

#### 4.1 Run the Lambda Function
```bash
# Invoke the ETL function
aws lambda invoke --function-name shop-etl-etl-function --profile your-profile-name output.json

# Check the results
cat output.json
```

**Expected Output:**
```py
{
  statusCode: 200,
  body: {
    "message": "...successfully",
    "records_processed": 30,
    "s3_key": "products/year=.../month=.../day=.../products_....csv",
    "execution_time": "2025...T....748402"
  }
}
```

#### 4.2 Run the Glue Crawler
```bash
# Start the crawler to catalog the data
aws glue start-crawler --name shop-products-crawler --profile your-profile-name

# Check crawler status
aws glue get-crawler --name shop-products-crawler --profile your-profile-name --query "Crawler.State"
```

Wait until status shows `"READY"` (usually 1-2 minutes). - it might even be less

#### 4.3 Query Data with Athena
```bash
# Get your bucket name from Terraform outputs
terraform output athena_results_bucket_name

# Run a test query
aws athena start-query-execution \
  --query-string "SELECT COUNT(*) as total_products FROM shop_products_db.products" \
  --result-configuration OutputLocation=s3://your-athena-results-bucket/query-results/ \
  --work-group shop-etl-workgroup \
  --profile your-profile-name
```

#### 4.4 Advanced Analytics Query
```sql
-- Query product categories and pricing
SELECT 
    price_category, 
    COUNT(*) as product_count,
    AVG(price) as avg_price,
    AVG(rating) as avg_rating
FROM shop_products_db.products 
GROUP BY price_category 
ORDER BY avg_price;
```

- you can create your own queries as well

## Understanding the Data Flow

### 1. Data Extraction
- Lambda function fetches product data from `https://dummyjson.com/products`
- Retrieves ~30 product records with details like price, rating, stock, etc.

### 2. Data Transformation
The Lambda function applies business logic:
- **Price Categories**: Budget (<$50), Mid ($50-$100), Premium ($100-$500), Luxury ($500+)
- **Rating Categories**: Fair (<4.0), Good (4.0-4.5), Excellent (4.5+)
- **Stock Status**: Out of Stock (0), Low Stock (<10), In Stock (10+)
- **Metadata**: Adds processing timestamp, data source, pipeline version

### 3. Data Storage
- Data stored in S3 with partitioned structure: `products/year=2024/month=9/day=3/`
- CSV format with headers for easy analysis

### 4. Schema Discovery
- Glue crawler automatically detects schema and data types
- Creates table `products` in database `shop_products_db`
- Supports partitioned querying for performance

### 5. Data Analysis
- Athena enables SQL queries directly on S3 data
- No data movement required - query in place
- Results stored in dedicated S3 bucket

## Monitoring and Troubleshooting

### Check Resource Status
```bash
# View all outputs
terraform output

# Check S3 bucket contents
aws s3 ls s3://your-bucket-name/products/ --recursive --profile your-profile-name

# Check Glue table schema
aws glue get-table --database-name shop_products_db --name products --profile your-profile-name
```

### Common Issues and Solutions

**Issue: Lambda timeout**
```bash
# Increase timeout in terraform.tfvars
lambda_timeout = 600  # 10 minutes

# Redeploy
python scripts/deploy.py apply
```

**Issue: S3 permissions error**
- Check that your AWS profile has S3 permissions
- Verify the bucket names in outputs

**Issue: Athena query fails**
- Ensure Glue crawler has completed
- Check that the table exists: `aws glue get-tables --database-name shop_products_db`

## Clean Up Resources

**IMPORTANT**: This will delete ALL resources and data!

```bash
# Run the destruction script
python scripts/destroy.py

# make sure you have the profile set in the script
# or you can start your profile with the prefix : "aws_profile"
# so "aws_profile_<your-name>"
```

The script will:
1. Empty all S3 buckets (data + query results)
2. Stop any running Athena queries
3. Clean up named queries
4. Destroy all 18 AWS resources with Terraform
5. Remove local state files

**Expected Output:**
```
Complete cleanup finished!
All AWS resources have been destroyed and local files cleaned up.
```

## Advanced Usage

### Customizing the ETL Logic
Edit `lambda/etl_function/lambda_function.py` to:
- Add new data transformations
- Change business rules for categorization
- Add data validation
- Connect to different APIs

### Scheduling ETL Jobs
Add EventBridge trigger to run ETL on schedule:
```hcl
# Add to lambda module
resource "aws_cloudwatch_event_rule" "etl_schedule" {
  name                = "etl-schedule"
  description         = "Run ETL daily"
  schedule_expression = "cron(0 2 * * ? *)"
}
```

### Adding More Data Sources
1. Extend the Lambda function
2. Update IAM permissions
3. Modify Glue crawler paths
4. Update Athena queries

## Security Considerations

- **IAM Roles**: Least privilege access patterns
- **S3 Security**: Block public access enabled