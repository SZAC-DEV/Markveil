"""Optional MCP stdio server. Install: pip install -e .[mcp].
MCP clients can request local filesystem access; only connect to trusted clients.
"""
from pathlib import Path
from .core import Options, create_preview, process_directory, SUPPORTED
from .comparison import compare_profiles
from .gallery_lab import gallery_test


def safe_output(source: Path, output: Path) -> tuple[Path, Path]:
    source, output = Path(source).expanduser().resolve(), Path(output).expanduser().resolve()
    if source == output or output.is_relative_to(source):
        raise ValueError("A saída deve estar fora da origem e não pode sobrescrever os originais.")
    if source.is_file() and output.is_relative_to(source.parent) and output.name == source.name:
        raise ValueError("Não sobrescreva o arquivo original.")
    return source, output


def preview_file(source: str, destination: str, text: str = 'PRÉVIA • NÃO COMPRADA', protection: str = 'adaptive', size: int = 1100, logo: str = '') -> dict:
    """Gera prévia marcada para um arquivo de imagem, preservando o original."""
    source_path, dest_path = safe_output(Path(source), Path(destination))
    if not source_path.is_file() or source_path.suffix.lower() not in SUPPORTED:
        raise ValueError('Origem deve ser uma fotografia válida.')
    if dest_path.suffix.lower() not in ('.jpg','.jpeg'):
        raise ValueError('Saída da prévia deve terminar em .jpg ou .jpeg.')
    return create_preview(source_path, dest_path, Options(text=text, protection=protection, max_size=size, logo_path=logo))


def preview_folder(source: str, destination: str, text: str = 'PRÉVIA • NÃO COMPRADA', protection: str = 'adaptive', size: int = 1100, logo: str = '') -> dict:
    """Marca um lote de fotos para uma pasta de saída separada."""
    inp, out = safe_output(Path(source), Path(destination))
    return process_directory(inp, out, Options(text=text, protection=protection, max_size=size, logo_path=logo))


def compare_file(source: str, destination: str) -> str:
    """Gera painel comparativo com os três perfis de proteção."""
    inp, out = safe_output(Path(source), Path(destination))
    return str(compare_profiles(inp,out,Options()))


def test_gallery(source: str, destination: str, protection: str = 'adaptive') -> dict:
    """Simula JPEG/resize e gera relatório. NÃO é benchmark de IA generativa."""
    inp, out = safe_output(Path(source), Path(destination))
    return gallery_test(inp,out,Options(protection=protection))


def main():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise SystemExit('Instale o suporte MCP: python -m pip install -e ".[mcp]"') from exc
    server = FastMCP('Markveil')
    server.tool()(preview_file)
    server.tool()(preview_folder)
    server.tool()(compare_file)
    server.tool()(test_gallery)
    server.run(transport='stdio')

if __name__ == '__main__': main()
