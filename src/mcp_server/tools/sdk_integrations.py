
import os
import boto3
from botocore.exceptions import ClientError
from google.cloud import storage
from azure.storage.blob import BlobServiceClient

import traceback

def aws_upload_s3(bucket: str, key: str, file_path: str):
    """
    Upload a file to AWS S3 bucket.
    Requires AWS credentials in environment.
    """
    try:
        s3 = boto3.client('s3')
        s3.upload_file(file_path, bucket, key)
        return {"status": "success", "bucket": bucket, "key": key}
    except ClientError as e:
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}

def gcp_list_bucket(bucket: str):
    """
    List files in a Google Cloud Storage bucket.
    Requires GCP credentials setup.
    """
    try:
        client = storage.Client()
        blobs = client.list_blobs(bucket)
        file_names = [blob.name for blob in blobs]
        return {"status": "success", "files": file_names}
    except Exception as e:
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}

def azure_download_blob(container: str, blob_name: str, download_path: str):
    """
    Download a blob from Azure Blob Storage container.
    Requires Azure connection string in env.
    """
    try:
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        container_client = blob_service_client.get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        return {"status": "success", "download_path": download_path}
    except Exception as e:
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
