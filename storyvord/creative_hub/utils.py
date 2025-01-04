import os
from azure.storage.blob import BlobServiceClient
import uuid

import logging

def handle_file_upload(file):
    logger = logging.getLogger(__name__)
    account_name = os.getenv('AZURE_ACCOUNT_NAMES')
    account_key = os.getenv('AZURE_ACCOUNT_KEYS')
    container_name = os.getenv('AZURE_CONTAINERS', 'your-container-name')

    if not account_name or not account_key:
        logger.error("Azure account credentials are missing in environment variables.")
        raise ValueError("Azure account credentials are missing in environment variables.")

    connection_string = (
        f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    )
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Ensure the container exists
    if not container_client.exists():
        container_client.create_container()
        logger.info(f"Created container {container_name}")

    blob_name = f"{uuid.uuid4()}_{file.name}"
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file, overwrite=True)
    logger.info(f"Uploaded file {blob_name} to {container_name}")

    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}"

