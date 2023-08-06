from unittest import TestCase
import futsu.hash as hash


class TestFs(TestCase):

    def test_md5_str(self):
        self.assertEqual(hash.md5_str('asdf'), '912ec803b2ce49e4a541068d495ab570')
        self.assertEqual(hash.md5_str(''), 'd41d8cd98f00b204e9800998ecf8427e')

    def test_sha256_str(self):
        self.assertEqual(hash.sha256_str('asdf'), 'f0e4c2f76c58916ec258f246851bea091d14d4247a2fc3e18694461b1816e13b')
        self.assertEqual(hash.sha256_str(''), 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
