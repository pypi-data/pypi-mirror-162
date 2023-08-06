from unittest import TestCase
import futsu.lazy_import as fli


class TestLazyImport(TestCase):

    def test_lazy_import(self):
        str_li = fli.lazy_import('string')
        str_m = str_li.load()
        self.assertEqual(str_m.digits, '0123456789')

        os_path_li = fli.lazy_import('os.path')
        os_path = os_path_li.load()
        os_path.join('a', 'b')
