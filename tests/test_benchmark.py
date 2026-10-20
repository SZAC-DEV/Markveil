import tempfile
import unittest
from pathlib import Path
from PIL import Image
from markveil.benchmark import benchmark_photo
from markveil.core import _sha256, Options

class TestBenchmark(unittest.TestCase):
    def test_benchmark_outputs_and_original_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            original=root/'inputs'/'image.png'; original.parent.mkdir()
            Image.new('RGB', (750,550), (30,125,210)).save(original)
            old_hash=_sha256(original)
            report=benchmark_photo(original,root/'report',Options(max_size=500))
            self.assertEqual(old_hash,_sha256(original))
            self.assertEqual(len(report['variants']),3)
            self.assertTrue((root/'report'/'index.html').is_file())
            self.assertTrue((root/'report'/'benchmark.json').is_file())
            self.assertIn('Não mede',report['limitations'])
    def test_refuse_output_under_original_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            original=root/'img.jpg'
            Image.new('RGB',(100,100)).save(original)
            with self.assertRaises(ValueError):
                benchmark_photo(original,root/'report')
