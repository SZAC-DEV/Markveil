from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_public_docs_exist():
    for name in ('README.md', 'docs/MCP.md', 'docs/RELEASING.md', 'docs/ARCHITECTURE.md', 'docs/TROUBLESHOOTING.md', 'docs/README.en.md', 'CONTRIBUTING.md'):
        assert (ROOT/name).is_file(), name

def test_readme_links_exist():
    for name in ('docs/MCP.md', 'docs/RELEASING.md', 'docs/ARCHITECTURE.md', 'docs/TROUBLESHOOTING.md', 'docs/README.en.md', 'LICENSE'):
        assert (ROOT/name).exists()
