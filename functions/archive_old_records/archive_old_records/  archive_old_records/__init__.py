import datetime
import logging
import os
import json
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import azure.functions as func

COSMOS_URI = os.getenv("COSMOS_URI")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB = os.getenv("COSMOS_DB")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER")
BLOB_CONN_STR = os.getenv("BLOB_CONN_STR")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER")

client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
database = client.get_database_client(COSMOS_DB)
container = database.get_container_client(COSMOS_CONTAINER)
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
blob_container_client = blob_service_client.get_container_client(BLOB_CONTAINER)

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Archival Function triggered')
    threshold_date = datetime.datetime.utcnow() - datetime.timedelta(days=90)
    query = f"SELECT * FROM c WHERE c.timestamp < '{threshold_date.isoformat()}'"

    for item in container.query_items(query=query, enable_cross_partition_query=True):
        record_id = item['id']
        partition_key = item['partitionKey']
        blob_name = f"{record_id}.json"

        blob_container_client.upload_blob(blob_name, json.dumps(item), overwrite=True)

        stub = {
            'id': record_id,
            'partitionKey': partition_key,
            'archived': True,
            'archiveUri': f"https://{blob_service_client.account_name}.blob.core.windows.net/{BLOB_CONTAINER}/{blob_name}"
        }
        container.upsert_item(stub)

        logging.info(f"Archived record {record_id} to blob and replaced with stub.")
