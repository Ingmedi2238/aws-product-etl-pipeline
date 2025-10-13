# AWS Product ETL Pipeline

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

A data engineering pipeline that extracts product data from DummyJSON API, processes it with AWS Lambda, stores it in S3, and makes it queryable through AWS Glue and Amazon Athena.