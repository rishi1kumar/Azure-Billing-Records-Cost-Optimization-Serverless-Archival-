import os
import json
import logging
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

def main(req: func.HttpRequest) -> func.HttpResponse:
    record_id = req.params.get('id')
    partition_key = req.params.get('partitionKey')

    if not record_id or not partition_key:
        return func.HttpResponse("Missing id or partitionKey", status_code=400)

    try:
        item = container.read_item(item=record_id, partition_key=partition_key)

        if item.get("archived"):
            blob_name = item["archiveUri"].split("/")[-1]
            blob = blob_container_client.download_blob(blob_name)
            data = blob.readall()
            return func.HttpResponse(data, mimetype="application/json")

        return func.HttpResponse(json.dumps(item), mimetype="application/json")

    except Exception as e:
        logging.error(f"Error retrieving record: {e}")
        return func.HttpResponse("Error retrieving record", status_code=500)
