import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from photoguard.adversarial import AdversarialConfig, protect_preview

class ExperimentalTests(unittest.TestCase):
    def test_valid_configuration(self):
        AdversarialConfig().validate()
    def test_invalid_epsilon(self):
        with self.assertRaises(ValueError): AdversarialConfig(epsilon=30).validate()
    def test_invalid_dimension(self):
        with self.assertRaises(ValueError): AdversarialConfig(size=513).validate()
    def test_refuses_overwrite_even_without_torch(self):
        with TemporaryDirectory() as folder:
            p=Path(folder)/'input.png';p.write_bytes(b'sample')
            with self.assertRaises(ValueError): protect_preview(p,p)
    def test_requires_png_output(self):
        with TemporaryDirectory() as folder:
            p=Path(folder)/'input.png';p.write_bytes(b'sample')
            with self.assertRaises(ValueError): protect_preview(p,Path(folder)/'result.jpg')
if __name__=='__main__': unittest.main()
