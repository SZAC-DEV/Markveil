import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from markveil.attack_lab import attack_test
from markveil.core import Options, _sha256

class TestAttackLab(unittest.TestCase):
    def test_external_attack_report_preserves_original(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); inp=root/'inputs';inp.mkdir()
            source=inp/'foto.png'
            Image.new('RGB',(250,180),(120,60,40)).save(source)
            before=_sha256(source)
            attack=root/'edited.png'
            Image.new('RGB',(250,180),(120,60,40)).save(attack)
            out=root/'report'
            data=attack_test(source,out,Options(max_size=320),attacked=attack)
            self.assertEqual(data['mode'],'external_attack_image')
            self.assertEqual(_sha256(source),before)
            self.assertTrue((out/'attack_report.html').is_file())
            self.assertTrue((out/'attack_mask.png').is_file())
            self.assertEqual(json.loads((out/'attack_report.json').read_text())['version'],'0.4.0')
            self.assertGreaterEqual(data['pixel_error_reduction_percent'],0)
    def test_reject_original_directory_and_no_mode(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); img=root/'photo.jpg';Image.new('RGB',(50,50)).save(img)
            with self.assertRaises(ValueError): attack_test(img,root/'report',attacked=img)
            with self.assertRaises(ValueError): attack_test(img,root.parent/'different_report')
    def test_opencv_local_optional(self):
        try: import cv2
        except ImportError: self.skipTest('opencv opcional não instalado')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); inp=root/'inputs';inp.mkdir();img=inp/'test.jpg'
            Image.new('RGB',(200,150),(80,90,110)).save(img)
            result=attack_test(img,root/'out',Options(max_size=320),local_inpaint=True)
            self.assertEqual(result['mode'],'opencv_telea_non_ai')
