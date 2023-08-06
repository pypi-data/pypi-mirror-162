import futsu
import futsu.lazy_import
import os

fgcpstorage_li = futsu.lazy_import.lazy_import('futsu.gcp.storage')
gcstorage_li = futsu.env_lazy_import('FUTSU_GCP_ENABLE', 'google.cloud.storage')
fs3_li = futsu.lazy_import.lazy_import('futsu.aws.s3')
ffs_li = futsu.lazy_import.lazy_import('futsu.fs')
urllib_request_li = futsu.lazy_import.lazy_import('urllib.request')
shutil_li = futsu.lazy_import.lazy_import('shutil')


def local_to_path(dst, src):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    ffs = ffs_li.load()
    if fgcpstorage.is_blob_path(dst):
        gcstorage = gcstorage_li.load()
        gcs_client = gcstorage.client.Client()
        fgcpstorage.file_to_blob(dst, src, gcs_client)
        return
    if fs3.is_blob_path(dst):
        client = fs3.create_client()
        fs3.file_to_blob(dst, src, client)
        return
    ffs.cp(dst, src)


def path_to_local(dst, src):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    ffs = ffs_li.load()
    if fgcpstorage.is_blob_path(src):
        gcstorage = gcstorage_li.load()
        gcs_client = gcstorage.client.Client()
        fgcpstorage.blob_to_file(dst, src, gcs_client)
        return
    if fs3.is_blob_path(src):
        client = fs3.create_client()
        fs3.blob_to_file(dst, src, client)
        return
    if src.startswith('https://') or src.startswith('http://'):
        urllib_request = urllib_request_li.load()
        with urllib_request.urlopen(src) as w_in, open(dst, 'wb') as f_out:
            shutil = shutil_li.load()
            shutil.copyfileobj(w_in, f_out)
        return
    ffs.cp(dst, src)


def bytes_to_path(dst, bytes):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    ffs = ffs_li.load()
    if fgcpstorage.is_blob_path(dst):
        gcstorage = gcstorage_li.load()
        gcs_client = gcstorage.client.Client()
        fgcpstorage.bytes_to_blob(dst, bytes, gcs_client)
        return
    if fs3.is_blob_path(dst):
        client = fs3.create_client()
        fs3.bytes_to_blob(dst, bytes, client)
        return
    ffs.bytes_to_file(dst, bytes)


def path_to_bytes(src):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    ffs = ffs_li.load()
    if fgcpstorage.is_blob_path(src):
        gcstorage = gcstorage_li.load()
        gcs_client = gcstorage.client.Client()
        return fgcpstorage.blob_to_bytes(src, gcs_client)
    if fs3.is_blob_path(src):
        client = fs3.create_client()
        return fs3.blob_to_bytes(src, client)
    if src.startswith('https://') or src.startswith('http://'):
        urllib_request = urllib_request_li.load()
        with urllib_request.urlopen(src) as w_in:
            return w_in.read()
    return ffs.file_to_bytes(src)


def is_blob_exist(p):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    if fgcpstorage.is_blob_path(p):
        gcstorage = gcstorage_li.load()
        gcs_client = gcstorage.client.Client()
        return fgcpstorage.is_blob_exist(p, gcs_client)
    if fs3.is_blob_path(p):
        client = fs3.create_client()
        return fs3.is_blob_exist(p, client)
    return os.path.isfile(p)


def rm(p):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    if fgcpstorage.is_blob_path(p):
        gcstorage = gcstorage_li.load()
        gcs_client = gcstorage.client.Client()
        return fgcpstorage.blob_rm(p, gcs_client)
    if fs3.is_blob_path(p):
        client = fs3.create_client()
        return fs3.blob_rm(p, client)
    return os.remove(p)


def find(p):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    ffs = ffs_li.load()
    if fgcpstorage.is_blob_path(p):
        gcstorage = gcstorage_li.load()
        gcs_client = gcstorage.client.Client()
        return fgcpstorage.find_blob_itr(p, gcs_client)
    if fs3.is_blob_path(p):
        client = fs3.create_client()
        return fs3.find_blob_itr(p, client)
    return ffs.find_file(p)


def join(*args):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    if fgcpstorage.is_path(args[0]):
        return fgcpstorage.join(*args)
    if fs3.is_path(args[0]):
        return fs3.join(*args)
    if args[0].startswith('https://') or args[0].startswith('http://'):
        return '/'.join(args)
    return os.path.join(*args)


def split(p):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    if fgcpstorage.is_path(p):
        return fgcpstorage.split(p)
    if fs3.is_path(p):
        return fs3.split(p)
    if p.startswith('https://') or p.startswith('http://'):
        return (dirname(p), basename(p))
    return os.path.split(p)


def basename(p):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    if fgcpstorage.is_path(p):
        return fgcpstorage.basename(p)
    if fs3.is_path(p):
        return fs3.basename(p)
    if p.startswith('https://') or p.startswith('http://'):
        return p[p.rindex('/')+1:]
    return os.path.basename(p)


def dirname(p):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    if fgcpstorage.is_path(p):
        return fgcpstorage.dirname(p)
    if fs3.is_path(p):
        return fs3.dirname(p)
    if p.startswith('https://') or p.startswith('http://'):
        return p[:p.rindex('/')]
    return os.path.dirname(p)


def rmtree(p):
    fgcpstorage = fgcpstorage_li.load()
    fs3 = fs3_li.load()
    if fgcpstorage.is_path(p):
        gcstorage = gcstorage_li.load()
        gcs_client = gcstorage.client.Client()
        fgcpstorage.rmtree(p, gcs_client)
    if fs3.is_path(p):
        client = fs3.create_client()
        fs3.rmtree(p, client)
    if p.startswith('https://') or p.startswith('http://'):
        raise Exception('CVALHPEH http(s) not support rmtree')
    shutil = shutil_li.load()
    shutil.rmtree(p, ignore_errors=True)
