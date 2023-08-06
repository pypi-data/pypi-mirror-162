import futsu
import futsu.aws as faws
import futsu.lazy_import
import re
boto3_li = futsu.env_lazy_import('FUTSU_AWS_ENABLE', 'boto3')
io_li = futsu.lazy_import.lazy_import('io')
botocore_exceptions_li = futsu.env_lazy_import('FUTSU_AWS_ENABLE', 'botocore.exceptions')

BUCKET_PATH_FORMAT = 's3://([^/]+)/?'
BUCKET_PATH_FORMAT_RE = None


def init_BUCKET_PATH_FORMAT_RE():
    global BUCKET_PATH_FORMAT_RE
    if BUCKET_PATH_FORMAT_RE is None:
        BUCKET_PATH_FORMAT_RE = re.compile(BUCKET_PATH_FORMAT)


BLOB_PATH_FORMAT = 's3://([^/]+)/(.+)'
BLOB_PATH_FORMAT_RE = None


def init_BLOB_PATH_FORMAT_RE():
    global BLOB_PATH_FORMAT_RE
    if BLOB_PATH_FORMAT_RE is None:
        BLOB_PATH_FORMAT_RE = re.compile(BLOB_PATH_FORMAT)


def is_bucket_path(path):
    init_BUCKET_PATH_FORMAT_RE()
    return BUCKET_PATH_FORMAT_RE.fullmatch(path) is not None


def is_blob_path(path):
    init_BLOB_PATH_FORMAT_RE()
    return BLOB_PATH_FORMAT_RE.fullmatch(path) is not None


def is_path(path):
    return is_bucket_path(path) or is_blob_path(path)


def prase_bucket_path(path):
    init_BUCKET_PATH_FORMAT_RE()
    m = BUCKET_PATH_FORMAT_RE.fullmatch(path)
    if not m:
        raise ValueError()
    return m.group(1)


def prase_blob_path(path):
    init_BLOB_PATH_FORMAT_RE()
    m = BLOB_PATH_FORMAT_RE.fullmatch(path)
    if not m:
        raise ValueError()
    return m.group(1), m.group(2)


def create_client(region_name=None):
    if region_name is None:
        if faws.default_region_name is not None:
            region_name = faws.default_region_name
    return boto3_li.load().client('s3')

# def bucket(gs_path, client):
#    bucket_name = prase_bucket_path(gs_path)
#    return client.bucket(bucket_name)

# def blob(gs_path, client):
#    bucket_name, blob_name = prase_blob_path(gs_path)
#    return client.bucket(bucket_name).blob(blob_name)


def file_to_blob(dst, src, client):
    dst_bucket_name, dst_object_key = prase_blob_path(dst)
    client.upload_file(
        Filename=src,
        Bucket=dst_bucket_name,
        Key=dst_object_key,
    )


def blob_to_file(dst, src, client):
    src_bucket_name, src_object_key = prase_blob_path(src)
    client.download_file(
        Filename=dst,
        Bucket=src_bucket_name,
        Key=src_object_key,
    )


def bytes_to_blob(dst, bytes, client):
    dst_bucket_name, dst_object_key = prase_blob_path(dst)
    with io_li.load().BytesIO(bytes) as bout:
        client.upload_fileobj(
            Fileobj=bout,
            Bucket=dst_bucket_name,
            Key=dst_object_key,
        )


def blob_to_bytes(src, client):
    src_bucket_name, src_object_key = prase_blob_path(src)
    with io_li.load().BytesIO() as bin:
        client.download_fileobj(
            Fileobj=bin,
            Bucket=src_bucket_name,
            Key=src_object_key,
        )
        bytes = bin.getvalue()
    return bytes


def string_to_blob(dst, s, client):
    bytes_to_blob(dst, s.encode('utf8'), client)


def blob_to_string(src, client):
    return blob_to_bytes(src, client).decode('utf8')


def is_blob_exist(path, client):
    botocore_exceptions = botocore_exceptions_li.load()
    bucket_name, object_key = prase_blob_path(path)
    try:
        client.head_object(
            Bucket=bucket_name,
            Key=object_key,
        )
        return True
    except botocore_exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise e
    assert (False)


def blob_rm(path, client):
    bucket_name, object_key = prase_blob_path(path)
    client.delete_object(
        Bucket=bucket_name,
        Key=object_key,
    )


def set_blob_acl(path, acl, client):
    bucket_name, object_key = prase_blob_path(path)
    client.put_object_acl(
        Bucket=bucket_name,
        Key=object_key,
        ACL=acl,
    )


def find_blob_itr(prefix, client, **kwargs):
    bucket_name, object_key = prase_blob_path(prefix)
    continuationtoken = None
    my_kwargs = {}
    while True:
        my_kwargs = {}
        if continuationtoken is not None:
            my_kwargs['ContinuationToken'] = continuationtoken
        ret_list = client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=object_key,
            **kwargs,
            **my_kwargs,
        )
        continuationtoken = ret_list['NextContinuationToken'] if ('NextContinuationToken' in ret_list) else \
            None
        if 'Contents' in ret_list:
            ret_list = ret_list['Contents']
            ret_list = map(lambda i: 's3://{}/{}'.format(bucket_name, i['Key']), ret_list)
            for ret in ret_list:
                yield ret
        if continuationtoken is None:
            break


def join(*args):
    return '/'.join(args)


def split(p):
    return (dirname(p), basename(p))


def dirname(p):
    return p[:p.rindex('/')]


def basename(p):
    return p[p.rindex('/')+1:]


def rmtree(p, client):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_objects
    prefix = '{p}/'.format(p=p)
    bucket_name, object_key = prase_blob_path(prefix)
    continuationtoken = None
    my_kwargs = {}
    while True:
        my_kwargs = {}
        if continuationtoken is not None:
            my_kwargs['ContinuationToken'] = continuationtoken
        ret_list = client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=object_key,
            **my_kwargs,
        )
        continuationtoken = ret_list['NextContinuationToken'] if ('NextContinuationToken' in ret_list) else \
            None
        if 'Contents' in ret_list:
            object_list = ret_list['Contents']
            object_list = map(lambda i: {'Key': i['Key']}, object_list)
            object_list = list(object_list)
            print('MVLWQTFX object_list={object_list}'.format(object_list=object_list))
            delete_ret = client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': object_list},
            )
            if delete_ret.get('Errors', []):
                raise Exception('FUJYOQJW '+str(delete_ret['Errors']))
            if len(delete_ret['Deleted']) != len(object_list):
                raise Exception("YGNAUABR result_len={result_len} expected_len={expected_len}".format(
                  result_len=len(delete_ret['Deleted']), expected_len=len(object_list)
                ))
        if continuationtoken is None:
            break
