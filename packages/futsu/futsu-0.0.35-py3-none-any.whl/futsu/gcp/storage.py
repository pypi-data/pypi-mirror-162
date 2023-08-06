import re

BUCKET_PATH_FORMAT = 'gs://([^/]+)/?'
BUCKET_PATH_FORMAT_RE = None


def init_BUCKET_PATH_FORMAT_RE():
    global BUCKET_PATH_FORMAT_RE
    if BUCKET_PATH_FORMAT_RE is None:
        BUCKET_PATH_FORMAT_RE = re.compile(BUCKET_PATH_FORMAT)


BLOB_PATH_FORMAT = 'gs://([^/]+)/(.+)'
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


def bucket(gs_path, client):
    bucket_name = prase_bucket_path(gs_path)
    return client.bucket(bucket_name)


def blob(gs_path, client):
    bucket_name, blob_name = prase_blob_path(gs_path)
    return client.bucket(bucket_name).blob(blob_name)


def file_to_blob(dst, src, client):
    blob(dst, client).upload_from_filename(src)


def blob_to_file(dst, src, client):
    blob(src, client).download_to_filename(dst)


def string_to_blob(dst, s, client):
    blob(dst, client).upload_from_string(s.encode('utf8'))


def blob_to_string(src, client):
    return blob(src, client).download_as_bytes().decode('utf8')


def bytes_to_blob(dst, s, client):
    blob(dst, client).upload_from_string(s)


def blob_to_bytes(src, client):
    return blob(src, client).download_as_bytes()


def is_blob_exist(path, client):
    return blob(path, client).exists()


def blob_rm(path, client):
    b = blob(path, client)
    if b.exists():
        b.delete()


def find_blob_itr(prefix, client):
    bucket_name, blob_name = prase_blob_path(prefix)
    itr = client.list_blobs(bucket_name, prefix=blob_name)
    itr = map(lambda i: 'gs://{}/{}'.format(bucket_name, i.name), itr)
    return itr


def join(*args):
    return '/'.join(args)


def split(p):
    return (dirname(p), basename(p))


def dirname(p):
    return p[:p.rindex('/')]


def basename(p):
    return p[p.rindex('/')+1:]


def rmtree(prefix, client):
    bucket_name, blob_name = prase_blob_path('{prefix}/'.format(prefix=prefix))
    itr = client.list_blobs(bucket_name, prefix=blob_name)
    for blob in itr:
        blob.delete()
