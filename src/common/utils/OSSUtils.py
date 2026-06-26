from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
secret_id = os.getenv('OSS_SECRET_ID')
secret_key = os.getenv('OSS_SECRET_KEY')
region = os.getenv('OSS_REGION')

token = None
scheme = 'https'
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
ossClient = CosS3Client(config)

# 上传系统文件到oss systemFiles目录
def uploadSystemFileToOSS(fileName: str):
    root = os.path.dirname(os.path.dirname(os.getcwd()))
    filePath = f"{root}/static/tempFiles/{fileName}"
    with open(filePath, 'rb') as fp:
        try:
            response = ossClient.put_object(
                Bucket=f'frog-ai-{os.getenv("OSS_APPID")}',
                Body=fp,
                Key=f"systemFiles/{fileName}",
                StorageClass='STANDARD',
                EnableMD5=False
            )
            logging.info(f"成功上传 {fileName} 到 OSS,response:{response}")
        except Exception as e:
            logging.error(f"上传 {fileName} 到 OSS 失败: {e}")
            raise e

# 上传系统文件到oss userFiles目录
def uploadUserFileToOSS(fileName: str):
    root = os.getcwd()
    filePath = f"{root}/static/tempFiles/{fileName}"
    with open(filePath, 'rb') as fp:
        try:
            response = ossClient.put_object(
                Bucket=f'frog-ai-{os.getenv("OSS_APPID")}',
                Body=fp,
                Key=f"userFiles/{fileName}",
                StorageClass='STANDARD',
                EnableMD5=False
            )
            logging.info(f"成功上传 {fileName} 到 OSS,response:{response}")
        except Exception as e:
            logging.error(f"上传 {fileName} 到 OSS 失败: {e}")
            raise e

# 获取oss systemFiles目录文件的URL
def getSystemFileUrl(fileName: str) -> str:
    try:
        response = ossClient.get_presigned_url(
            Bucket=f'frog-ai-{os.getenv("OSS_APPID")}',
            Key=f"systemFiles/{fileName}",
            Method='GET',
            Expired=300
        )
        logging.info(f"成功获取 {fileName} 的 URL,response:{response}")
        return response
    except Exception as e:
        logging.error(f"获取 {fileName} 的 URL 失败: {e}")
        raise e

# 获取oss userFiles目录文件的URL
def getUserFileUrl(fileName: str) -> str:
    try:
        response = ossClient.get_presigned_url(
            Bucket=f'frog-ai-{os.getenv("OSS_APPID")}',
            Key=f"userFiles/{fileName}",
            Method='POST',
            Expired=300
        )
        logging.info(f"成功获取 {fileName} 的 URL,response:{response}")
        return response
    except Exception as e:
        logging.error(f"获取 {fileName} 的 URL 失败: {e}")
        raise e

