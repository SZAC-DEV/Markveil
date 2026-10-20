import sys
from pathlib import Path
from markveil.settings import platform_config_dir

def test_user_config_override(tmp_path, monkeypatch):
    monkeypatch.setenv('MARKVEIL_CONFIG_DIR',str(tmp_path/'prefs'))
    assert platform_config_dir() == tmp_path/'prefs'

def test_config_default(monkeypatch):
    monkeypatch.delenv('MARKVEIL_CONFIG_DIR',raising=False)
    location=platform_config_dir()
    assert location.name.lower() == 'markveil'

def test_build_scripts_exist():
    root=Path(__file__).resolve().parents[1]
    for item in ('build_windows.bat','build_linux.sh','build_macos.sh','iniciar_linux.sh','iniciar_macos.command'):
        assert (root/item).is_file()

def test_entrypoints_available():
    import markveil.cli, markveil.gui, markveil.mcp_server
    assert callable(markveil.cli.main)
    assert callable(markveil.gui.main)
    assert callable(markveil.mcp_server.main)
