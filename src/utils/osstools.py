# -*- coding: utf-8 -*-  
"""
@Date     : 2024-08-22
@Author   : xwq
@Desc     : <None>

"""
import mimetypes
from io import BytesIO
import boto3
from botocore.client import BaseClient, Config
from botocore.exceptions import ClientError

from src.config import get_config


def _get_client() -> BaseClient:
    """
    获取client实例
    :return:
    """
    session: boto3.Session = boto3.session.Session()
    client: BaseClient = session.client(
        service_name='s3',
        aws_access_key_id=get_config('oss', 'access_key'),
        aws_secret_access_key=get_config('oss', 'secret_key'),
        endpoint_url=get_config('oss', 'endpoint'),
        config=Config(signature_version='s3v4', connect_timeout=180, read_timeout=180)
    )
    return client


def oss_upload(
        file_key: str,
        file_path: str
) -> str:
    """
    上传文件到oss
    :param file_key: 指定上传后的文件名
    :param file_path: 本地文件路径
    :return:
    """
    oss_dct: dict[str, str] = get_config('oss')
    client: BaseClient = _get_client()
    # 使用 mimetypes 获取 MIME 类型
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'  # 默认的 MIME 类型
    client.upload_file(file_path, oss_dct['bucket'], file_key,
                       ExtraArgs={'ContentType': content_type})
    return f"{oss_dct['endpoint'].rstrip('/')}/{oss_dct['bucket']}/{file_key}"


def compose_oss_url(oss_key: str) -> str:
    """
    组装oss全链接
    :param oss_key:
    :return:
    """
    oss_dct: dict[str, str] = get_config('oss')
    return f"{oss_dct['endpoint'].rstrip('/')}/{oss_dct['bucket']}/{oss_key}"


# 其他函数保持不变


def oss_download(
        file_key: str,
        file_path: str
) -> None:
    """
    下载文件
    :param file_key: 在桶中的文件名
    :param file_path:
    :return:
    """
    client: BaseClient = _get_client()
    client.download_file(get_config('oss', 'bucket'), file_key, file_path)


def oss_exists(
        file_key: str
) -> bool:
    """
    查询桶内是否存在该文件
    :param file_key:
    :return:
    """
    client: BaseClient = _get_client()
    try:
        client.head_object(Bucket=get_config('oss', 'bucket'), Key=file_key)
        return True
    except ClientError:
        return False


def oss_download_bytes(file_key: str) -> BytesIO:
    """
    下载指定key的文件，以字节流的形式
    :param file_key:
    :return:
    """
    client: BaseClient = _get_client()
    obj: BytesIO = BytesIO()
    client.download_fileobj(get_config('oss', 'bucket'), file_key, obj)

    return obj


def _test():
    upload_path = 'D:/test.jpg'
    download_path = 'D:/test2.jpg'
    import uuid
    file_key = str(uuid.uuid4())
    oss_upload(file_key, upload_path)
    oss_download(file_key, download_path)


def _test2():
    oss_download('4564e731-db01-44a8-907c-157ff3dbedac', 'D:/test3.jpg')


if __name__ == '__main__':
    # _test()
    _test2()
    pass
