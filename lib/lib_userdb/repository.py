import os
from datetime import datetime, timezone

import aioboto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "urls")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DYNAMODB_ENDPOINT_URL = os.environ.get("DYNAMODB_ENDPOINT_URL")

_session = aioboto3.Session()


def _dynamodb_kwargs() -> dict:
    kwargs = {"region_name": AWS_REGION}
    if DYNAMODB_ENDPOINT_URL:
        kwargs["endpoint_url"] = DYNAMODB_ENDPOINT_URL
    return kwargs


async def query_by_original_url(original_url: str) -> dict | None:
    async with _session.resource("dynamodb", **_dynamodb_kwargs()) as dynamodb:
        table = await dynamodb.Table(TABLE_NAME)
        response = await table.query(
            IndexName="original_url-index",
            KeyConditionExpression=Key("original_url").eq(original_url),
            Limit=1,
        )
        items = response.get("Items", [])
        return items[0] if items else None


async def query_by_short_url(short_url: str) -> dict | None:
    async with _session.resource("dynamodb", **_dynamodb_kwargs()) as dynamodb:
        table = await dynamodb.Table(TABLE_NAME)
        response = await table.get_item(Key={"short_url": short_url})
        return response.get("Item")


async def insert_url(original_url: str, short_url: str) -> None:
    async with _session.resource("dynamodb", **_dynamodb_kwargs()) as dynamodb:
        table = await dynamodb.Table(TABLE_NAME)
        await table.put_item(
            Item={
                "short_url": short_url,
                "original_url": original_url,
                "count": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            ConditionExpression="attribute_not_exists(short_url)",
        )


async def increment_count(short_url: str) -> None:
    async with _session.resource("dynamodb", **_dynamodb_kwargs()) as dynamodb:
        table = await dynamodb.Table(TABLE_NAME)
        await table.update_item(
            Key={"short_url": short_url},
            UpdateExpression="SET #c = #c + :inc",
            ExpressionAttributeNames={"#c": "count"},
            ExpressionAttributeValues={":inc": 1},
        )
