# DynamoDB Table Definition
#
# Table: urls
#   Partition Key : short_url    (String)
#   Attributes    : original_url (String)
#                   count        (Number)
#                   created_at   (String, ISO-8601)
#
# GSI: original_url-index
#   Partition Key : original_url (String)
#   Projection    : ALL
#
# boto3 equivalent:
#
# client.create_table(
#     TableName="urls",
#     KeySchema=[
#         {"AttributeName": "short_url", "KeyType": "HASH"},
#     ],
#     AttributeDefinitions=[
#         {"AttributeName": "short_url",    "AttributeType": "S"},
#         {"AttributeName": "original_url", "AttributeType": "S"},
#     ],
#     GlobalSecondaryIndexes=[
#         {
#             "IndexName": "original_url-index",
#             "KeySchema": [{"AttributeName": "original_url", "KeyType": "HASH"}],
#             "Projection": {"ProjectionType": "ALL"},
#         }
#     ],
#     BillingMode="PAY_PER_REQUEST",
# )
