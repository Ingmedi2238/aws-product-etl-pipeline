"""
Configuration settings for the ETL Lambda function
"""

class Config:
    # API Configuration
    BASE_ROUTE = 'https://dummyjson.com'
    PRODUCTS_ENDPOINT = f'{BASE_ROUTE}/products'
    
    # Data Processing Configuration
    DATA_SOURCE = 'dummyjson_api'
    PIPELINE_VERSION = '1.0'
    
    # Request Configuration
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # Data Validation
    REQUIRED_COLUMNS = [
        'id', 'title', 'price', 'rating', 
        'stock', 'brand', 'category'
    ]
    
    # Price Categories
    PRICE_BINS = [0, 50, 100, 500, float('inf')]
    PRICE_LABELS = ['Budget', 'Mid', 'Premium', 'Luxury']
    
    # Rating Thresholds
    EXCELLENT_RATING = 4.5
    GOOD_RATING = 4.0
    
    # Stock Thresholds  
    LOW_STOCK_THRESHOLD = 10
    OUT_OF_STOCK = 0