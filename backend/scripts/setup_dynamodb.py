import boto3
import os
from dotenv import load_dotenv

# Load env
load_dotenv(os.path.join(os.getcwd(), ".env"), override=True)

def create_table():
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    table_name = "educorp_skills"
    
    print(f"Creating table {table_name} in {region}...")
    
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'pk', 'KeyType': 'HASH'},  # Partition key
                {'AttributeName': 'sk', 'KeyType': 'RANGE'}  # Sort key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pk', 'AttributeType': 'S'},
                {'AttributeName': 'sk', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        print("Table status:", table.table_status)
        print("Waiting for table to exist...")
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print("Table created successfully!")
        
    except Exception as e:
        if "ResourceInUseException" in str(e):
            print("Table already exists.")
        else:
            print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_table()
