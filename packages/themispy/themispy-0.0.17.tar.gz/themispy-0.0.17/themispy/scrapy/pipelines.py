# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
from io import BytesIO

from azure.storage.blob import BlobClient
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.misc import md5sum

from themispy.project.utils import split_filepath


class AzureBlobUploadPipeline:
    """
    Custom class created in order to upload blobs to Azure Storage.
    The connection to Azure Storage is made during the 'open_spider'
    method and the blob upload is made during the 'close_spider' method
    in the Item Pipeline.
    Blob name defaults to "{spider.name}.jsonl" and the container name
    is retrieved from "AZCONTAINER_PATH" environment variable.
    """
    def open_spider(self, spider):
        self.blob_client = BlobClient.from_connection_string(
            conn_str=os.environ['AzureWebJobsStorage'],
            container_name=os.environ['AZCONTAINER_PATH'],
            blob_name=f"{spider.name}.jsonl",
            logging_enable=True)
        
        self.content = ''

    
    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + '\n'
        self.content += line
        return item

    
    def close_spider(self, spider):
        self.blob_client.upload_blob(data=self.content, overwrite=True)


class AzureFileDownloaderPipeline(FilesPipeline):
    """
    Custom class created in order to upload downloaded files to
    Azure Storage. Even though you don't actually store downloaded
    files locally, you still must pass a 'FILES_STORE' value to your
    spider settings.
    """
    def file_downloaded(self, response, request, info, *, item=None):
        # path = self.file_path(request, response=response, info=info, item=item)
        buf = BytesIO(response.body)
        checksum = md5sum(buf)
        buf.seek(0)
        
        
        # Azure Integration
        docname, docext = split_filepath(response.url)
        
        self.blob_client = BlobClient.from_connection_string(
            conn_str=os.environ['AzureWebJobsStorage'],
            container_name=os.environ['AZCONTAINER_PATH'],
            blob_name=f"{docname}{docext}",
            logging_enable=True)
        
        self.blob_client.upload_blob(data=buf, overwrite=True)
        
        
        # self.store.persist_file(path, buf, info)
        return checksum
