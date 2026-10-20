# Solução de problemas

| Sintoma | Diagnóstico / correção |
|---|---|
| `No module named markveil` | Ative `.venv` e execute `python -m pip install -e .` na raiz do projeto |
| `No module named tkinter` no Linux | Instale pacote `python3-tk` ou equivalente e recrie/reative a venv |
| Janela fecha ao iniciar | Inicie com `python -m markveil.gui` no terminal e anexe o traceback à issue |
| Arrastar/soltar não funciona | Instale extra `.[desktop]`; use o botão de selecionar pasta; teste X11/Wayland/macOS separadamente |
| Barra de GPU sem dados | Confirme `nvidia-smi` no PATH e driver NVIDIA; GPU AMD/Intel/Apple não é monitorada da mesma forma |
| `markveil` não é reconhecido | Use `python -m markveil` ou ative o ambiente virtual |
| Permissão negada na pasta de saída | Escolha destino gravável, fora da origem |
| Preset não carrega | Confira `presets.json` no diretório de configuração do sistema e valide JSON |
| `pip` falha por ambiente gerenciado (Linux/macOS) | Crie/ative `python3 -m venv .venv`; não use `sudo pip` |
| macOS avisa sobre app não verificado | `.app` ainda não foi assinado/notarizado; use instalação por código-fonte verificado ou aguarde release assinada |
| MCP desconecta | Garanta interpretador correto na configuração do cliente e biblioteca `mcp` instalada; use `stdio` |
| Interface corta conteúdo em resolução baixa | Maximize/ajuste escala do monitor; reporte resolução exata para evolução responsiva |

Ao abrir uma issue, informe: SO e versão, arquitetura, versão do Python, passos para reproduzir, traceback, modelo de GPU (se relevante) e exemplo sintético de imagem sem dados pessoais.
