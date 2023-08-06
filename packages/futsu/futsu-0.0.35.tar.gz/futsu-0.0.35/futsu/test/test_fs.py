from unittest import TestCase
import futsu.fs as fs
import tempfile
import os


class TestFs(TestCase):

    def test_makedirs(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_dirname = os.path.join(tempdir, 'JBMLJUBDTQ', 'TJLQSLRTJL')
            self.assertFalse(os.path.isdir(tmp_dirname))
            fs.makedirs(tmp_dirname)
            self.assertTrue(os.path.isdir(tmp_dirname))
            fs.makedirs(tmp_dirname)  # test run 2 times
            self.assertTrue(os.path.isdir(tmp_dirname))

    def test_reset_dir(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_dirname = os.path.join(tempdir, 'JUEJKVTEJR', 'TYEAWJIQSN')
            tmp_filename = os.path.join(tmp_dirname, 'JEWKHIDKCU')

            self.assertFalse(os.path.isdir(tmp_dirname))
            self.assertFalse(os.path.isfile(tmp_filename))

            fs.reset_dir(tmp_dirname)  # test create tmp_dirname
            self.assertTrue(os.path.isdir(tmp_dirname))
            self.assertFalse(os.path.isfile(tmp_filename))

            with open(tmp_filename, 'wt') as fout:
                fout.write('\n')
            self.assertTrue(os.path.isdir(tmp_dirname))
            self.assertTrue(os.path.isfile(tmp_filename))

            fs.reset_dir(tmp_dirname)  # test clean tmp_filename
            self.assertTrue(os.path.isdir(tmp_dirname))
            self.assertFalse(os.path.isfile(tmp_filename))

    def test_diff(self):
        self.assertFalse(fs.diff(
            os.path.join('futsu', 'test', 'test_diff_0.txt'),
            os.path.join('futsu', 'test', 'test_diff_1.txt')
        ))
        self.assertTrue(fs.diff(
            os.path.join('futsu', 'test', 'test_diff_0.txt'),
            os.path.join('futsu', 'test', 'test_diff_2.txt')
        ))

    def test_cp(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir, 'YHGASBIGHI')
            fs.cp(
                tmp_filename,
                os.path.join('futsu', 'test', 'test_cp_0.txt')
            )
            self.assertFalse(fs.diff(
                tmp_filename,
                os.path.join('futsu', 'test', 'test_cp_0.txt')
            ))

    def test_file_to_string_list(self):
        line_list = fs.file_to_string_list(os.path.join('futsu', 'test', 'test_fs_0.txt'))
        self.assertEqual(line_list, ['qwer', 'asdf'])

        line_list = fs.file_to_string_list(os.path.join('futsu', 'test', 'test_fs_1.txt'))
        self.assertEqual(line_list, ['qwer', 'asdf'])

        line_list = fs.file_to_string_list(os.path.join('futsu', 'test', 'test_fs_2.txt'))
        self.assertEqual(line_list, ['qwer', 'asdf', ''])

    def test_string_list_to_file(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir, 'PRXNBTESJS')

            line_list = ['qwer', 'asdf']
            fs.string_list_to_file(tmp_filename, line_list)
            self.assertEqual(line_list, ['qwer', 'asdf'])

            line_list = ['qwer', 'asdf', '']
            fs.string_list_to_file(tmp_filename, line_list)
            self.assertEqual(line_list, ['qwer', 'asdf', ''])

    def test_file_bytes_io(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir, 'INUDYDVGRH')

            fs.bytes_to_file(tmp_filename, 'UIIUAZUNNF'.encode('utf-8'))
            txt = fs.file_to_bytes(tmp_filename).decode('utf-8')
            self.assertEqual(txt, 'UIIUAZUNNF')

    def test_find_file(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename_list = [os.path.join(tempdir, 'ISEZHQOQ-{0}'.format(i)) for i in range(10)]
            for tmp_filename in tmp_filename_list:
                fs.bytes_to_file(tmp_filename, b'')

            file_list = fs.find_file(tempdir)
            file_list = list(file_list)
            self.assertEqual(len(file_list), 10)
            file_list = sorted(file_list)
            self.assertEqual(file_list, tmp_filename_list)

    def test_is_dir(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_path = os.path.join(tempdir, 'ELCAWJBE')
            self.assertFalse(fs.is_dir(tmp_path))
            fs.makedirs(tmp_path)
            self.assertTrue(fs.is_dir(tmp_path))

            tmp_path = os.path.join(tempdir, 'MATKBCNT')
            self.assertFalse(fs.is_dir(tmp_path))
            fs.bytes_to_file(tmp_path, b'')
            self.assertFalse(fs.is_dir(tmp_path))

    def test_is_file(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_path = os.path.join(tempdir, 'AMBLRDNO')
            self.assertFalse(fs.is_file(tmp_path))
            fs.makedirs(tmp_path)
            self.assertFalse(fs.is_file(tmp_path))

            tmp_path = os.path.join(tempdir, 'XCYMJDNI')
            self.assertFalse(fs.is_file(tmp_path))
            fs.bytes_to_file(tmp_path, b'')
            self.assertTrue(fs.is_file(tmp_path))

    def test_is_exist(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_path = os.path.join(tempdir, 'XWYPDSVT')
            self.assertFalse(fs.is_exist(tmp_path))
            fs.makedirs(tmp_path)
            self.assertTrue(fs.is_exist(tmp_path))

            tmp_path = os.path.join(tempdir, 'MRAMKBJC')
            self.assertFalse(fs.is_exist(tmp_path))
            fs.bytes_to_file(tmp_path, b'')
            self.assertTrue(fs.is_exist(tmp_path))

    def test_rm_dir(self):
        with tempfile.TemporaryDirectory() as tempdir:
            # rm not exist
            tmp_path = os.path.join(tempdir, 'HYVPLFZA')
            fs.rm_dir(tmp_path)

            # rm dir
            tmp_path = os.path.join(tempdir, 'RLZIEDFY')
            fs.makedirs(tmp_path)
            fs.rm_dir(tmp_path)
            self.assertFalse(fs.is_dir(tmp_path))

            # rm file
            tmp_path = os.path.join(tempdir, 'KQDGCKDS')
            fs.bytes_to_file(tmp_path, b'')
            self.assertRaises(ValueError, fs.rm_dir, tmp_path)

    def test_rm_file(self):
        with tempfile.TemporaryDirectory() as tempdir:
            # rm not exist
            tmp_path = os.path.join(tempdir, 'DBSJBLOD')
            fs.rm_file(tmp_path)

            # rm dir
            tmp_path = os.path.join(tempdir, 'TXZGCGFO')
            fs.makedirs(tmp_path)
            self.assertRaises(ValueError, fs.rm_file, tmp_path)

            # rm file
            tmp_path = os.path.join(tempdir, 'NUFIPTJA')
            fs.bytes_to_file(tmp_path, b'')
            fs.rm_file(tmp_path)
            self.assertFalse(fs.is_file(tmp_path))

    def test_rm(self):
        with tempfile.TemporaryDirectory() as tempdir:
            # rm not exist
            tmp_path = os.path.join(tempdir, 'UFIUJLKN')
            fs.rm_file(tmp_path)

            # rm dir
            tmp_path = os.path.join(tempdir, 'JMGSKISO')
            fs.makedirs(tmp_path)
            fs.rm_dir(tmp_path)
            self.assertFalse(fs.is_dir(tmp_path))

            # rm file
            tmp_path = os.path.join(tempdir, 'RNNUTMLB')
            fs.bytes_to_file(tmp_path, b'')
            fs.rm_file(tmp_path)
            self.assertFalse(fs.is_file(tmp_path))
