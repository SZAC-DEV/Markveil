# Markveil Studio

**Open-source, local-first photographic preview protection.**

Markveil generates watermarked preview photographs for photographers and galleries without modifying source files. It offers a desktop application, CLI, optional MCP server and experiments for local gallery transformations. **No watermark is guaranteed to survive generative removal tools.**

> [!IMPORTANT]
> Markveil is independent of MadryLab's PhotoGuard research project. Adversarial experiments are optional and not verified protection claims. Third-party platforms may generate their own watermarks and might not permit custom previews.

## Quick start · Windows

Requires Python 3.10+. Extract the repository then double-click `iniciar_windows.bat`.

```powershell
py -m pip install -e .
markveil gui
```

## CLI

```powershell
markveil protect "C:\Fotos" "C:\Previas" --protection strong
markveil compare "C:\Fotos\foto.jpg" "C:\Relatorios\comparison.jpg"
markveil gallery-test "C:\Fotos\foto.jpg" "C:\Relatorios"
markveil benchmark "C:\Fotos\foto.jpg" "C:\Relatorios"
markveil --help
```

`classic`, `adaptive` and `strong` are visual watermark presets, not quantitatively certified AI resistance levels. Output must be separate from originals.

## MCP (stdio)

```powershell
py -m pip install -e ".[mcp]"
markveil mcp
```

Tools: `preview_file`, `preview_folder`, `compare_file`, `test_gallery`. Local MCP clients can request filesystem operations; **connect only trusted clients**. See `examples/mcp-client-config.json`.

## Development

```powershell
py -m pip install -e . pytest
py -m pytest -q
```

Optional attack tests: `pip install -e ".[attack]"`. Optional adversarial experimentation: `pip install -e ".[adversarial]"` (large dependencies/model download).

## Windows executable

Run `build_windows.bat` on Windows, which invokes PyInstaller. The resulting Windows executable has not been validated in this environment.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Changes should include tests and avoid overwriting user images. Use clearly stated metrics when discussing AI-resistance.

## License

MIT. Refer to [LICENSE](LICENSE).


## Interface v0.10.0
Escolha a pasta de fotos, clique **CARREGAR FOTOGRAFIAS**, selecione uma imagem na lista e use **ATUALIZAR PRÉVIA**. A prévia aparece dentro da janela. **PROTEGER TODAS AS FOTOS** processa o lote e exibe progresso.

O aplicativo não implementa arrastar e soltar nativo nesta versão; selecione a pasta pelo botão.


## v0.11 — Desktop improvements

Install optional desktop extras with `py -3 -m pip install -e ".[desktop]"` on Windows, then run `py -3 -m markveil.gui`. The application tries to launch maximized and includes before/after comparison slider, optional drag and drop, presets and optional resource metrics. The NVIDIA telemetry shows system-wide GPU utilization, **not GPU compute attributed to Markveil**; standard watermarking is CPU-based. GPU is used only for relevant experimental model runs when supported. CLI and MCP entrypoints remain unchanged.

Windows exe: run `build_windows.bat` on Windows with Python installed. Generated executables have not been tested in this environment.


## v0.12 · Windows / Linux / macOS

**Código único, builds nativos por sistema.** Python 3.10+ e Tk são necessários para rodar a interface a partir do código. Em algumas distribuições Linux é preciso instalar `python3-tk` pelo gerenciador de pacotes.

- **Windows:** `iniciar_windows.bat`; `build_windows.bat` cria o EXE no próprio Windows.
- **Linux:** `./iniciar_linux.sh`; `./build_linux.sh` gera um binário Linux. Pode requerer pacotes Tk e bibliotecas gráficas do sistema.
- **macOS:** `./iniciar_macos.command` (ou `zsh iniciar_macos.command`); `./build_macos.sh` gera um `.app` **no próprio macOS**. Distribuição a outras pessoas requer assinatura e notarização Apple para evitar avisos Gatekeeper.
- **CLI:** `markveil --help` em qualquer sistema; funciona em máquinas sem display.
- **MCP:** `markveil mcp` em qualquer sistema, via stdio, quando o extra `[mcp]` estiver instalado.
- **Presets:** `%APPDATA%\Markveil` (Windows), `~/Library/Application Support/Markveil` (macOS), `$XDG_CONFIG_HOME/markveil` ou `~/.config/markveil` (Linux). Override para testes: `MARKVEIL_CONFIG_DIR`.
- **GPU:** métricas NVIDIA quando `nvidia-smi` estiver disponível. O processamento convencional usa CPU. Em Macs com Apple Silicon, o processamento adversarial requer validação específica de MPS, não garantida.

O workflow do GitHub Actions executa testes nos três sistemas; builds podem ser criados manualmente com `workflow_dispatch`. Builds produzidos na CI **não** são automaticamente assinados, notarizados ou validados visualmente.
