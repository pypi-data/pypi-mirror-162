# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
from io import BytesIO

from azure.storage.blob import ContainerClient, BlobClient
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.misc import md5sum

from themispy.project.utils import get_logpath, split_filepath


class AzureBlobUploadPipeline:
    """
    Custom class created in order to upload blobs to Azure Storage
    using default spider crawling.
    """
    def open_spider(self, spider):
        print(f"Opening Blob Client@Container<'{os.environ['AZCONTAINER_PATH']}'>.")
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
    def open_spider(self, spider):
        self.spiderinfo = self.SpiderInfo(spider)
        
        print(f"Opening Container Client@<'{os.environ['AZCONTAINER_PATH']}'>.")
        self.container_client = ContainerClient.from_connection_string(
            conn_str=os.environ['AzureWebJobsStorage'],
            container_name=os.environ['AZCONTAINER_PATH'],
            logging_enable=True)
        
    
    def file_downloaded(self, response, request, info, *, item=None):
        path = self.file_path(request, response=response, info=info, item=item)
        buf = BytesIO(response.body)
        checksum = md5sum(buf)
        buf.seek(0)
        
        
        # Naming Settings
        PROJECT_TITLE = os.path.split(
            os.environ['AZCONTAINER_PATH'].strip(get_logpath()))[-1]
        
        docname, docext = split_filepath(response.url)
        
        # Azure Integration
        self.blob_client = self.container_client.get_blob_client(
            blob=f"{PROJECT_TITLE}_{docname}{docext}")
        
        self.blob_client.upload_blob(data=buf, overwrite=True, logging_enable=True)
        
        
        self.store.persist_file(path, buf, info)
        return checksum
