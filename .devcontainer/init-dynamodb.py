"""
Creates the DynamoDB `urls` table (with GSI) against DynamoDB Local.
Run once after the container starts: python .devcontainer/init-dynamodb.py
"""

import os
import time

import boto3
from botocore.exceptions import ClientError

ENDPOINT_URL = os.environ.get("DYNAMODB_ENDPOINT_URL", "http://dynamodb-local:8001")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "urls")
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")


def wait_for_dynamodb(client, retries: int = 10, delay: float = 2.0) -> None:
    for attempt in range(1, retries + 1):
        try:
            client.list_tables()
            print("DynamoDB Local is ready.")
            return
        except Exception:
            print(f"Waiting for DynamoDB Local... ({attempt}/{retries})")
            time.sleep(delay)
    raise RuntimeError("DynamoDB Local did not become ready in time.")


def create_table(client) -> None:
    try:
        client.create_table(
            TableName=TABLE_NAME,
            AttributeDefinitions=[
                {"AttributeName": "short_url", "AttributeType": "S"},
                {"AttributeName": "original_url", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "short_url", "KeyType": "HASH"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "original_url-index",
                    "KeySchema": [
                        {"AttributeName": "original_url", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5,
                    },
                }
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5,
            },
        )
        print(f"Table '{TABLE_NAME}' created successfully.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"Table '{TABLE_NAME}' already exists — skipping.")
        else:
            raise


if __name__ == "__main__":
    client = boto3.client(
        "dynamodb",
        region_name=REGION,
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
    )
    wait_for_dynamodb(client)
    create_table(client)
