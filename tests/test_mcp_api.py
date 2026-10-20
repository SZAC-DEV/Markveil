from pathlib import Path
import pytest
from PIL import Image
from markveil.mcp_server import safe_output, preview_file, preview_folder

def test_prevent_overwrite(tmp_path):
    path=tmp_path/'a.jpg'
    path.write_bytes(b'hi')
    with pytest.raises(ValueError): safe_output(path,path)
    with pytest.raises(ValueError): safe_output(tmp_path,tmp_path/'sub')

def test_preview_file(tmp_path):
    src=tmp_path/'photo.png'; dest=tmp_path/'out'/'photo.jpg'
    Image.new('RGB',(450,350),'orange').save(src)
    before=src.read_bytes()
    preview_file(str(src),str(dest))
    assert dest.exists() and src.read_bytes()==before

def test_bad_output(tmp_path):
    src=tmp_path/'photo.png';Image.new('RGB',(450,350)).save(src)
    with pytest.raises(ValueError):preview_file(str(src),str(tmp_path/'out.png'))
