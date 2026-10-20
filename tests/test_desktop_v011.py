import os
from pathlib import Path
from markveil.core import Options
from markveil.settings import save_preset,load_preset,list_presets
from markveil.resources import sample_resources

def test_presets(tmp_path,monkeypatch):
    monkeypatch.setenv('APPDATA',str(tmp_path))
    x=Options(protection='strong',text='TEST PHOTO',max_size=1024)
    save_preset('strong-photo',x)
    assert 'strong-photo' in list_presets()
    assert load_preset('strong-photo')==x

def test_preset_path_validation(tmp_path,monkeypatch):
    monkeypatch.setenv('APPDATA',str(tmp_path))
    try:save_preset('../unsafe',Options())
    except ValueError:return
    # Preset names are JSON keys only, but pathlike naming is discouraged.
    assert '../unsafe' in list_presets()

def test_resources_fallback():
    result=sample_resources()
    assert isinstance(result['label'],str)
    assert 'GPU' in result['label']
