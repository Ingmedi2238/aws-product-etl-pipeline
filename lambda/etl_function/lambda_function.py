import json
import boto3
import requests
import pandas as pd
from datetime import datetime
import logging
import os
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AWS clients
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Main Lambda handler for ETL pipeline
    Extracts product data from DummyJSON API, transforms it, and loads to S3
    """
    try:
        logger.info("Starting ETL pipeline execution")
        
        # Extract data from API
        products = extract_products_data()
        logger.info(f"Extracted {len(products)} products from API")
        
        # Transform the data
        df = transform_products_data(products)
        logger.info(f"Transformed data: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Load data to S3
        s3_key = load_data_to_s3(df)
        logger.info(f"Data successfully loaded to S3: {s3_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'ETL pipeline completed successfully',
                'records_processed': len(products),
                's3_key': s3_key,
                'execution_time': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'ETL pipeline failed',
                'message': str(e),
                'execution_time': datetime.now().isoformat()
            })
        }

def extract_products_data():
    """
    Extract product data from DummyJSON API
    """
    try:
        response = requests.get(Config.PRODUCTS_ENDPOINT, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        products = data.get('products', [])
        
        if not products:
            raise ValueError("No products found in API response")
            
        logger.info("Successfully extracted data from DummyJSON API")
        return products
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch data from API: {str(e)}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Invalid API response format: {str(e)}")
        raise

def transform_products_data(products):
    """
    Transform the raw products data into a structured format
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(products)
        
        # Select key columns
        required_columns = ['id', 'title', 'price', 'rating', 'stock', 'brand', 'category']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"Missing columns in data: {missing_columns}")
            # Add missing columns with default values
            for col in missing_columns:
                df[col] = None
        
        df = df[required_columns]
        
        # Handle missing values
        df = df.fillna({
            'price': 0.0,
            'rating': 0.0,
            'stock': 0,
            'brand': 'Unknown',
            'category': 'Unknown'
        })
        
        # Ensure correct data types
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)
        df['stock'] = pd.to_numeric(df['stock'], errors='coerce').fillna(0)
        
        # Business transformations
        # Add price category
        df['price_category'] = pd.cut(
            df['price'], 
            bins=[0, 50, 100, 500, float('inf')], 
            labels=['Budget', 'Mid', 'Premium', 'Luxury'],
            right=False
        )
        
        # Add rating category
        df['rating_category'] = df['rating'].apply(
            lambda x: 'Excellent' if x >= 4.5 else ('Good' if x >= 4.0 else 'Fair')
        )
        
        # Add stock status
        df['stock_status'] = df['stock'].apply(
            lambda x: 'Out of Stock' if x == 0 else ('Low Stock' if x < 10 else 'In Stock')
        )
        
        # Add metadata columns
        df['processed_at'] = datetime.now().isoformat()
        df['data_source'] = Config.DATA_SOURCE
        df['pipeline_version'] = Config.PIPELINE_VERSION
        
        logger.info("Data transformation completed successfully")
        return df
        
    except Exception as e:
        logger.error(f"Data transformation failed: {str(e)}")
        raise

def load_data_to_s3(df):
    """
    Load the transformed data to S3 bucket
    """
    try:
        # Convert DataFrame to CSV
        csv_data = df.to_csv(index=False)
        
        # Generate S3 key with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_key = f"products/year={datetime.now().year}/month={datetime.now().month:02d}/day={datetime.now().day:02d}/products_{timestamp}.csv"
        
        # Upload to S3
        bucket_name = os.environ.get('S3_BUCKET_NAME')
        if not bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable not set")
        
        s3.put_object(
            Body=csv_data.encode('utf-8'),
            Bucket=bucket_name,
            Key=s3_key,
            ContentType='text/csv'
        )
        
        logger.info(f"Data successfully uploaded to S3: s3://{bucket_name}/{s3_key}")
        return s3_key
        
    except Exception as e:
        logger.error(f"Failed to upload data to S3: {str(e)}")
        raise

# For testing purposes
if __name__ == "__main__":
    # Test the lambda function locally
    test_event = {}
    test_context = {}
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2))