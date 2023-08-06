from unittest import TestCase
from futsu.gcp import storage as fstorage
import futsu.fs as ffs
import tempfile
import os
from google.cloud import storage as gcstorage
import time
import string
import random


class TestStorage(TestCase):

    def test_is_bucket_path(self):
        self.assertTrue(fstorage.is_bucket_path('gs://bucket'))
        self.assertTrue(fstorage.is_bucket_path('gs://bucket/'))

        self.assertFalse(fstorage.is_bucket_path('gs://bucket//'))
        self.assertFalse(fstorage.is_bucket_path('gs://bucket/asdf'))
        self.assertFalse(fstorage.is_bucket_path('gs://bucket/asdf/'))
        self.assertFalse(fstorage.is_bucket_path('gs://bucket/asdf/asdf'))

        self.assertFalse(fstorage.is_bucket_path('s://bucket'))
        self.assertFalse(fstorage.is_bucket_path('g://bucket'))
        self.assertFalse(fstorage.is_bucket_path('gs//bucket'))
        self.assertFalse(fstorage.is_bucket_path('gs:/bucket'))
        self.assertFalse(fstorage.is_bucket_path('gs://'))
        self.assertFalse(fstorage.is_bucket_path('gs:///'))
        self.assertFalse(fstorage.is_bucket_path('gs:///asdf'))

    def test_is_blob_path(self):
        self.assertFalse(fstorage.is_blob_path('gs://bucket'))
        self.assertFalse(fstorage.is_blob_path('gs://bucket/'))

        self.assertTrue(fstorage.is_blob_path('gs://bucket//'))
        self.assertTrue(fstorage.is_blob_path('gs://bucket/asdf'))
        self.assertTrue(fstorage.is_blob_path('gs://bucket/asdf/'))
        self.assertTrue(fstorage.is_blob_path('gs://bucket/asdf/asdf'))

        self.assertFalse(fstorage.is_blob_path('s://bucket'))
        self.assertFalse(fstorage.is_blob_path('g://bucket'))
        self.assertFalse(fstorage.is_blob_path('gs//bucket'))
        self.assertFalse(fstorage.is_blob_path('gs:/bucket'))
        self.assertFalse(fstorage.is_blob_path('gs://'))
        self.assertFalse(fstorage.is_blob_path('gs:///'))
        self.assertFalse(fstorage.is_blob_path('gs:///asdf'))

    def test_is_path(self):
        self.assertTrue(fstorage.is_path('gs://bucket'))
        self.assertTrue(fstorage.is_path('gs://bucket/'))

        self.assertTrue(fstorage.is_path('gs://bucket//'))
        self.assertTrue(fstorage.is_path('gs://bucket/asdf'))
        self.assertTrue(fstorage.is_path('gs://bucket/asdf/'))
        self.assertTrue(fstorage.is_path('gs://bucket/asdf/asdf'))

        self.assertFalse(fstorage.is_path('s://bucket'))
        self.assertFalse(fstorage.is_path('g://bucket'))
        self.assertFalse(fstorage.is_path('gs//bucket'))
        self.assertFalse(fstorage.is_path('gs:/bucket'))
        self.assertFalse(fstorage.is_path('gs://'))
        self.assertFalse(fstorage.is_path('gs:///'))
        self.assertFalse(fstorage.is_path('gs:///asdf'))

    def test_parse_bucket_path(self):
        self.assertEqual(fstorage.prase_bucket_path('gs://asdf'), 'asdf')
        self.assertRaises(ValueError, fstorage.prase_bucket_path, 'asdf')

    def test_prase_blob_path(self):
        self.assertEqual(fstorage.prase_blob_path('gs://asdf/qwer'), ('asdf', 'qwer'))
        self.assertEqual(fstorage.prase_blob_path('gs://asdf/qwer/'), ('asdf', 'qwer/'))
        self.assertRaises(ValueError, fstorage.prase_blob_path, 'asdf')

    def test_gcp_string(self):
        token = '{ts}-{r}'.format(ts=int(time.time()), r=randstr())
        tmp_gs_path = 'gs://futsu-test/test-LAVVKOIHAT-{0}'.format(token)

        client = gcstorage.client.Client()
        fstorage.string_to_blob(tmp_gs_path, 'JLPUSLMIHV', client)
        s = fstorage.blob_to_string(tmp_gs_path, client)
        self.assertEqual(s, 'JLPUSLMIHV')

    def test_gcp_bytes(self):
        token = '{ts}-{r}'.format(ts=int(time.time()), r=randstr())
        tmp_gs_path = 'gs://futsu-test/test-SCALNUVEVQ-{0}'.format(token)

        client = gcstorage.client.Client()
        fstorage.bytes_to_blob(tmp_gs_path, b'VUOUWXZNIA', client)
        s = fstorage.blob_to_bytes(tmp_gs_path, client)
        self.assertEqual(s, b'VUOUWXZNIA')

    def test_gcp_file(self):
        client = gcstorage.client.Client()
        with tempfile.TemporaryDirectory() as tempdir:
            token = '{ts}-{r}'.format(ts=int(time.time()), r=randstr())
            src_fn = os.path.join('futsu', 'gcp', 'test', 'test_storage.txt')
            tmp_gs_path = 'gs://futsu-test/test-CQJWTXYXEJ-{0}'.format(token)
            tmp_filename = os.path.join(tempdir, 'PKQXWFJWRB')

            fstorage.file_to_blob(tmp_gs_path, src_fn, client)
            fstorage.blob_to_file(tmp_filename, tmp_gs_path, client)

            self.assertFalse(ffs.diff(src_fn, tmp_filename))

    def test_exist(self):
        token = '{ts}-{r}'.format(ts=int(time.time()), r=randstr())
        tmp_gs_path = 'gs://futsu-test/test-NKLUNOKTWZ-{0}'.format(token)

        client = gcstorage.client.Client()
        self.assertFalse(fstorage.is_blob_exist(tmp_gs_path, client))
        fstorage.string_to_blob(tmp_gs_path, 'DQJDDJMULZ', client)
        self.assertTrue(fstorage.is_blob_exist(tmp_gs_path, client))

    def test_delete(self):
        token = '{ts}-{r}'.format(ts=int(time.time()), r=randstr())
        tmp_gs_path = 'gs://futsu-test/test-EYVNPCTBAH-{0}'.format(token)

        client = gcstorage.client.Client()

        self.assertFalse(fstorage.is_blob_exist(tmp_gs_path, client))

        fstorage.blob_rm(tmp_gs_path, client)

        self.assertFalse(fstorage.is_blob_exist(tmp_gs_path, client))

        fstorage.string_to_blob(tmp_gs_path, 'BHAHMMJVYF', client)
        self.assertTrue(fstorage.is_blob_exist(tmp_gs_path, client))

        fstorage.blob_rm(tmp_gs_path, client)

        self.assertFalse(fstorage.is_blob_exist(tmp_gs_path, client))

    def test_find_blob_itr(self):
        client = gcstorage.client.Client()
        token = '{ts}-{r}'.format(ts=int(time.time()), r=randstr())
        tmp_gs_path_list = ['gs://futsu-test/test-QMKOGJVS-{0}/{1}'.format(token, i) for i in range(10)]
        for tmp_gs_path in tmp_gs_path_list:
            fstorage.bytes_to_blob(tmp_gs_path, b'TBJSUSIE', client)

        blob_list = fstorage.find_blob_itr('gs://futsu-test/test-QMKOGJVS-{0}/'.format(token), client)
        blob_list = list(blob_list)
        self.assertEqual(len(blob_list), 10)
        blob_list = sorted(blob_list)
        self.assertEqual(blob_list, tmp_gs_path_list)

    def test_join(self):
        self.assertEqual(fstorage.join('gs://NARNEHCQ', 'UDGTMPFX'), 'gs://NARNEHCQ/UDGTMPFX')
        self.assertEqual(fstorage.join('gs://NARNEHCQ', 'UDGTMPFX', 'AFOCASQL'), 'gs://NARNEHCQ/UDGTMPFX/AFOCASQL')

    def test_split(self):
        self.assertEqual(fstorage.split('gs://NARNEHCQ/UDGTMPFX'), ('gs://NARNEHCQ', 'UDGTMPFX'))
        self.assertEqual(fstorage.split('gs://NARNEHCQ/UDGTMPFX/AFOCASQL'), ('gs://NARNEHCQ/UDGTMPFX', 'AFOCASQL'))

    def test_dirname(self):
        self.assertEqual(fstorage.dirname('gs://NARNEHCQ/UDGTMPFX'), 'gs://NARNEHCQ')
        self.assertEqual(fstorage.dirname('gs://NARNEHCQ/UDGTMPFX/AFOCASQL'), 'gs://NARNEHCQ/UDGTMPFX')

    def test_basename(self):
        self.assertEqual(fstorage.basename('gs://NARNEHCQ/UDGTMPFX'), 'UDGTMPFX')
        self.assertEqual(fstorage.basename('gs://NARNEHCQ/UDGTMPFX/AFOCASQL'), 'AFOCASQL')

    def test_rmtree(self):
        token = '{ts}-{r}'.format(ts=int(time.time()), r=randstr())
        path0 = 'gs://futsu-test/test-HOSPFEUB-{token}'.format(token=token)
        path00 = fstorage.join(path0, 'ITGDLUVB')
        path000 = fstorage.join(path00, 'WKBXFDTH', 'CMCXBJYN')
        path001 = fstorage.join(path00, 'MGNZJTXL', 'RGWIYPEG')
        path01 = fstorage.join(path0, 'GMZSNRPD', 'UOAUKUKG', 'VJUOXIQY')
        path02 = fstorage.join(path0, 'ITGDLUVBx')

        gcs_client = gcstorage.client.Client()

        fstorage.bytes_to_blob(path000, b'', gcs_client)
        fstorage.bytes_to_blob(path001, b'', gcs_client)
        fstorage.bytes_to_blob(path01, b'', gcs_client)
        fstorage.bytes_to_blob(path02, b'', gcs_client)

        self.assertTrue(fstorage.is_blob_exist(path000, gcs_client))
        self.assertTrue(fstorage.is_blob_exist(path001, gcs_client))
        self.assertTrue(fstorage.is_blob_exist(path01, gcs_client))
        self.assertTrue(fstorage.is_blob_exist(path02, gcs_client))

        fstorage.rmtree(path00, gcs_client)

        self.assertFalse(fstorage.is_blob_exist(path000, gcs_client))
        self.assertFalse(fstorage.is_blob_exist(path001, gcs_client))
        self.assertTrue(fstorage.is_blob_exist(path01, gcs_client))
        self.assertTrue(fstorage.is_blob_exist(path02, gcs_client))


def randstr():
    charset = list(set(string.ascii_letters) | set(string.digits))
    return "".join(random.choice(charset)for x in range(8))
