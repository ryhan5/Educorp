import boto3
import os

REGION_NAME = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
TABLE_PREFIX = os.getenv("DYNAMODB_TABLE_PREFIX", "educorp")

try:
    dynamodb = boto3.resource("dynamodb", region_name=REGION_NAME)
except Exception as e:
    print(f"Error initializing DynamoDB resource: {e}")
    dynamodb = None

def get_table_name(base_name: str) -> str:
    return f"{TABLE_PREFIX}_{base_name}"

def init_tables():
    """
    Creates necessary DynamoDB tables if they don't exist.
    """
    if not dynamodb:
        print("DynamoDB resource not available.")
        return

    # 1. SkillGraph Table
    skill_graph_table = get_table_name("SkillGraph")
    create_table_if_not_exists(
        table_name=skill_graph_table,
        key_schema=[
            {'AttributeName': 'user_id', 'KeyType': 'HASH'},  # Partition Key
            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'} # Sort Key
        ],
        attribute_definitions=[
            {'AttributeName': 'user_id', 'AttributeType': 'S'},
            {'AttributeName': 'timestamp', 'AttributeType': 'S'}
        ]
    )

    # 2. Users Table
    users_table = get_table_name("Users")
    create_table_if_not_exists(
        table_name=users_table,
        key_schema=[
            {'AttributeName': 'user_id', 'KeyType': 'HASH'}
        ],
        attribute_definitions=[
            {'AttributeName': 'user_id', 'AttributeType': 'S'}
        ]
    )

def create_table_if_not_exists(table_name, key_schema, attribute_definitions):
    try:
        table = dynamodb.Table(table_name)
        table.load()
        print(f"Table {table_name} already exists.")
    except Exception:
        print(f"Creating table {table_name}...")
        try:
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"Table {table_name} creating...")
            table.wait_until_exists()
            print(f"Table {table_name} created successfully.")
        except Exception as e:
             print(f"Failed to create table {table_name}: {e}")
