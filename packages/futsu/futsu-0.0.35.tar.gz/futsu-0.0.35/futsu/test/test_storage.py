from unittest import TestCase
import futsu.storage as storage
import tempfile
import os
import futsu.fs as fs
import time
import futsu.json
import json
import random
import string


class TestStorage(TestCase):

    def test_local(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir, 'QKDQXVOOME')
            src_file = os.path.join('futsu', 'test', 'test_storage_0.txt')

            self.assertFalse(storage.is_blob_exist(tmp_filename))

            storage.local_to_path(tmp_filename, src_file)
            self.assertTrue(storage.is_blob_exist(tmp_filename))
            self.assertFalse(fs.diff(tmp_filename, src_file))

            storage.rm(tmp_filename)
            self.assertFalse(storage.is_blob_exist(tmp_filename))

            tmp_filename = os.path.join(tempdir, 'NKNVMMYPUI')
            bytes0 = b'YENLUMVECW'
            storage.bytes_to_path(tmp_filename, bytes0)
            bytes1 = storage.path_to_bytes(tmp_filename)
            self.assertEqual(bytes0, bytes1)

            tmp_root_path = os.path.join(tempdir, 'BDHYVQKO')
            fs.makedirs(tmp_root_path)
            tmp_path_list = [os.path.join(tmp_root_path, '{0}'.format(i)) for i in range(10)]
            for tmp_path in tmp_path_list:
                storage.bytes_to_path(tmp_path, b'')
            ret_path_list = storage.find(tmp_root_path)
            ret_path_list = sorted(list(ret_path_list))
            self.assertEqual(ret_path_list, tmp_path_list)

    def test_gcp(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir, 'GPVRUHXTTC')
            src_file = os.path.join('futsu', 'test', 'test_storage_0.txt')
            token = '{ts}-{r}'.format(ts=int(time.time()), r=randstr())
            tmp_gs_blob = 'gs://futsu-test/test-NXMUHBDEMR-{0}'.format(token)

            self.assertFalse(storage.is_blob_exist(tmp_gs_blob))

            storage.local_to_path(tmp_gs_blob, src_file)
            self.assertTrue(storage.is_blob_exist(tmp_gs_blob))

            storage.path_to_local(tmp_filename, tmp_gs_blob)
            self.assertFalse(fs.diff(tmp_filename, src_file))

            storage.rm(tmp_gs_blob)
            self.assertFalse(storage.is_blob_exist(tmp_gs_blob))

            tmp_gs_blob = 'gs://futsu-test/test-DQZFYPFNUV-{0}'.format(token)
            bytes0 = b'RZCPRGZZBC'
            storage.bytes_to_path(tmp_gs_blob, bytes0)
            bytes1 = storage.path_to_bytes(tmp_gs_blob)
            self.assertEqual(bytes0, bytes1)

            tmp_path_list = ['gs://futsu-test/test-NKMYDMGJ-{0}/{1}'.format(token, i) for i in range(10)]
            for tmp_path in tmp_path_list:
                storage.bytes_to_path(tmp_path, b'')
            ret_path_list = storage.find('gs://futsu-test/test-NKMYDMGJ-{0}/'.format(token))
            ret_path_list = sorted(list(ret_path_list))
            self.assertEqual(ret_path_list, tmp_path_list)

    def test_s3(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir, 'TMWGHOKDRE')
            src_file = os.path.join('futsu', 'test', 'test_storage_0.txt')
            token = '{ts}-{r}'.format(ts=int(time.time()), r=randstr())
            tmp_path = 's3://futsu-test/test-KWPIYZVIYK-{0}'.format(token)

            self.assertFalse(storage.is_blob_exist(tmp_path))

            storage.local_to_path(tmp_path, src_file)
            self.assertTrue(storage.is_blob_exist(tmp_path))

            storage.path_to_local(tmp_filename, tmp_path)
            self.assertFalse(fs.diff(tmp_filename, src_file))

            storage.rm(tmp_path)
            self.assertFalse(storage.is_blob_exist(tmp_path))

            tmp_gs_blob = 's3://futsu-test/test-LKUDEBPHEF-{0}'.format(token)
            bytes0 = b'SUZODZKFXW'
            storage.bytes_to_path(tmp_gs_blob, bytes0)
            bytes1 = storage.path_to_bytes(tmp_gs_blob)
            self.assertEqual(bytes0, bytes1)

            tmp_path_list = ['s3://futsu-test/test-SVABRZZM-{0}/{1}'.format(token, i) for i in range(10)]
            for tmp_path in tmp_path_list:
                storage.bytes_to_path(tmp_path, b'')
            ret_path_list = storage.find('s3://futsu-test/test-SVABRZZM-{0}/'.format(token))
            ret_path_list = sorted(list(ret_path_list))
            self.assertEqual(ret_path_list, tmp_path_list)

    def test_http(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir, 'RICFYWBCVI')

            tmp_path = 'https://httpbin.org/get'

            storage.path_to_local(tmp_filename, tmp_path)
            data = futsu.json.file_to_data(tmp_filename)
            self.assertEqual(data['url'], tmp_path)

            data = storage.path_to_bytes(tmp_path)
            data = json.loads(data.decode('utf-8'))
            self.assertEqual(data['url'], tmp_path)

            tmp_path = 'http://httpbin.org/get'

            storage.path_to_local(tmp_filename, tmp_path)
            data = futsu.json.file_to_data(tmp_filename)
            self.assertEqual(data['url'], tmp_path)

            data = storage.path_to_bytes(tmp_path)
            data = json.loads(data.decode('utf-8'))
            self.assertEqual(data['url'], tmp_path)


def randstr():
    charset = list(set(string.ascii_letters) | set(string.digits))
    return "".join(random.choice(charset)for x in range(8))
