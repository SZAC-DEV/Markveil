# Arquitetura do Markveil

## Visão geral

```text
Desktop (Tkinter) ─┐
CLI (argparse) ─────┼──> core.py (Options, create_preview, process_directory)
MCP (FastMCP) ──────┘               │
                         JPEGs reduzidos e marcados

comparison.py ──> comparação de perfis
gallery_lab.py ──> recompressão e resize + relatório
benchmark.py ────> análise de qualidade
attack_lab.py ────> ataques clássicos e importação de resultado externo
adversarial.py ───> experimento opcional dependente de modelos
settings.py ─────> JSON de presets por usuário
```

O **núcleo convencional é local e baseado em Pillow**, com formatos de entrada JPG/JPEG, PNG, WEBP, TIFF/TIF e BMP (dependem do suporte Pillow instalado). A saída normal é JPEG. A API interna trabalha com objetos `Options` imutáveis e valida faixas de parâmetros.

## Processamento

1. Abre origem e aplica orientação EXIF; 2. Converte para RGB; 3. Reduz imagem para o maior lado configurado; 4. Aplica texto/PNG, grade e perfil selecionado; 5. Grava destino separado.

**Limites:** sem garantia de segurança criptográfica ou DRM; qualquer visualizador que veja pixels pode capturá-los. Perturbações adversariais podem desaparecer após redimensionamento/JPEG e precisam de testes controlados.

## Compatibilidade e arquitetura de builds

Python 3.10+ / sistemas Windows, Linux, macOS. A aplicação desktop exige Tk/Tcl e opcionalmente `tkinterdnd2`; telemetria usa `psutil` e, em NVIDIA, CLI `nvidia-smi`. PyInstaller empacota para a arquitetura/OS da máquina de build, não gera binários cross-compiled. O macOS exige builds separados conforme necessidades Intel/Apple Silicon, ou um build universal devidamente testado.

## Mapa de código

`src/markveil/core.py`, `gui.py`, `cli.py`, `mcp_server.py`, `settings.py`, `resources.py` e laboratórios. `tests/` contém testes automatizados. `launcher.py` é a entrada do empacotador; `iniciar_*` são inicializadores para desenvolvimento; `build_*` são scripts de compilação.
