# Markveil Studio — English quick start

Markveil is an **open-source local-first tool** that generates visibly watermarked, reduced-resolution photo previews while preserving original image files. It offers a Tkinter desktop application, Python CLI and an optional MCP stdio server. **It does not guarantee protection against generative AI watermark removal.** Third-party photo galleries are not automatically integrated.

**Requirements:** Python 3.10+, Tk/Tcl for GUI, optional NVIDIA tools for GPU monitoring.

**Windows:** double-click `iniciar_windows.bat`, or create `.venv` and run `python -m pip install -e ".[desktop]"` followed by `python -m markveil.gui`.

**Linux:** install your distro's Tk and venv packages, then `bash iniciar_linux.sh`.

**macOS:** `zsh iniciar_macos.command` with Python/Tk installed.

**CLI:** `markveil protect ./originals ./previews --protection adaptive`.

**MCP:** `python -m pip install -e ".[mcp]"` and `markveil mcp`. It grants trusted clients access to local files. Read [MCP](MCP.md).

**Testing:** `python -m pip install pytest` then `python -m pytest -q`.

**Release building:** see [Release guide](RELEASING.md). Cross-platform automated tests do not guarantee working signed/installable GUI binaries.

The Portuguese [README](../README.md) is the authoritative full guide. MIT licensed.
