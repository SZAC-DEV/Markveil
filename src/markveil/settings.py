"""Persistent local settings for named preview profiles."""
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from .core import Options

def platform_config_dir():
    """User-specific writable preferences location on Windows, macOS and Linux."""
    override = os.environ.get('MARKVEIL_CONFIG_DIR')
    if override:
        return Path(override).expanduser()
    if sys.platform == 'win32':
        return Path(os.environ.get('APPDATA') or Path.home() / 'AppData' / 'Roaming') / 'Markveil'
    if sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'Markveil'
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / 'markveil'

def config_file():
    root=platform_config_dir()
    return root/'presets.json'

def _read():
    path=config_file()
    if not path.exists():return {}
    result=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(result,dict):raise ValueError('Arquivo de presets inválido')
    return result

def list_presets():
    return sorted(_read())

def save_preset(name, options):
    name=name.strip()
    if not name or len(name)>50:raise ValueError('Nome do preset deve ter de 1 a 50 caracteres.')
    options.validate()
    data=_read()
    data[name]=asdict(options)
    path=config_file();path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    temp.replace(path)

def load_preset(name):
    data=_read()
    if name not in data:raise ValueError('Preset não encontrado: '+name)
    result=Options(**data[name]);result.validate()
    return result
