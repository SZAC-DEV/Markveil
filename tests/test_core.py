import tempfile
import unittest
from pathlib import Path
from PIL import Image
from photoguard.core import Options, create_preview, process_directory, _sha256

class TestCore(unittest.TestCase):
    def test_generate_and_preserve_original(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            src=root/'source.jpg'; dst=root/'preview.jpg'
            Image.new('RGB',(2400,1600),'#7280a0').save(src)
            before=_sha256(src)
            result=create_preview(src,dst,Options(max_size=800))
            self.assertEqual(before,_sha256(src))
            self.assertTrue(dst.exists())
            with Image.open(dst) as img:
                self.assertEqual(max(img.size),800)
                self.assertFalse('exif' in img.info)
            self.assertEqual(result['source_sha256'],before)

    def test_reject_output_inside_originals(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'originals').mkdir()
            with self.assertRaises(ValueError):
                process_directory(root/'originals',root/'originals'/'preview',Options())

    def test_batch_and_duplicate_names(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); inp=root/'input';out=root/'output'; inp.mkdir()
            Image.new('RGB',(800,800),'red').save(inp/'same.jpg')
            Image.new('RGB',(800,800),'blue').save(inp/'same.png')
            result=process_directory(inp,out,Options())
            self.assertEqual(len(result['images']),2)
            self.assertTrue((out/'same_jpg_preview.jpg').exists())
            self.assertTrue((out/'same_png_preview.jpg').exists())

if __name__=='__main__':unittest.main()

class TestCustomLogo(unittest.TestCase):
    def test_logo_overlay_preserves_input(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            src=root/'photo.jpg'; dst=root/'marked.jpg'; logo=root/'logo.png'
            Image.new('RGB',(500,400),'gray').save(src)
            Image.new('RGBA',(100,40),(255,40,30,255)).save(logo)
            before=_sha256(src)
            create_preview(src,dst,Options(text='TESTE',logo_path=str(logo),logo_scale=30,grid=False))
            self.assertEqual(_sha256(src),before)
            self.assertTrue(dst.exists())
    def test_missing_png_rejected(self):
        with self.assertRaises(ValueError):
            Options(logo_path='/does-not-exist.png').validate()
