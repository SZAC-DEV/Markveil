from pathlib import Path
import hashlib
import json
import pytest
from PIL import Image
from photoguard.core import Options
from photoguard.gallery_lab import gallery_test


def test_gallery_report_preserves_source(tmp_path):
    source = tmp_path / 'originals' / 'teste.jpg'
    source.parent.mkdir()
    Image.new('RGB', (640, 420), '#667788').save(source)
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    dest = tmp_path / 'reports'
    result = gallery_test(source, dest, Options(protection='strong'))
    assert result['source_preserved'] is True
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert len(result['variants']) == 5
    assert (dest / 'index.html').exists()
    assert (dest / 'gallery-report.json').exists()
    assert all((dest / row['file']).exists() for row in result['variants'])
    assert all(row['difference_from_paired_clean_mae_0_255'] >= 0 for row in result['variants'])
    assert 'Não indicam' in result['caution']


def test_gallery_rejects_output_inside_originals(tmp_path):
    source = tmp_path / 'orig' / 'a.jpg'
    source.parent.mkdir()
    Image.new('RGB', (640, 480)).save(source)
    with pytest.raises(ValueError):
        gallery_test(source, source.parent / 'reports')


def test_html_escapes_filename(tmp_path):
    source = tmp_path / 'orig' / 'x&y.jpg'
    source.parent.mkdir()
    Image.new('RGB', (640, 480)).save(source)
    gallery_test(source, tmp_path / 'safe')
    assert 'x&amp;y.jpg' in (tmp_path / 'safe' / 'index.html').read_text(encoding='utf8')
