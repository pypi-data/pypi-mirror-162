import os

from azure.storage.blob import BlobClient


def read_jsonl(blob: str, attr: str = 'url', encoding: str = 'UTF-8',
               startswith: str = 'http') -> 'list[str]':
    """
    Reads all JSON Lines datasources from the specified
    blob and container.
    """
    attr = f'"{attr}": "'
    
    blob_client = BlobClient.from_connection_string(
        conn_str=os.environ['AzureWebJobsStorage'],
        container_name=os.environ['AZCONTAINER_PATH'],
        blob_name=blob,
        logging_enable=True)
    
    stream = blob_client.download_blob()
    content, datasources = [], []
    
    for i in stream.content_as_text(encoding=encoding).split(attr):
        if i.startswith(f"{startswith}"):
            content.append(i)
        
    for i in content:
        idx = i.find('"')
        i = i[:idx]
        datasources.append(i)
    
    return datasources
