# Markveil Studio

**Proteção local de prévias fotográficas · Desktop + CLI + MCP · Windows, Linux e macOS**

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue)](.github/workflows/tests.yml) ![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-beta-orange)

> **Versão 0.13.0 — beta.** Markveil gera **prévias com marca d'água**, sem modificar as fotografias originais. Marcas não são impossíveis de remover por IA: **não há taxa de proteção cientificamente validada**. A ferramenta não integra automaticamente galerias comerciais (Fotto, Fotop, Banlek etc.) e não processa pagamentos.

**Idioma:** Português (principal) · [English quick start](docs/README.en.md)

## Índice

1. [O que é e o que não é](#o-que-é-e-o-que-não-é)
2. [Funcionalidades](#funcionalidades)
3. [Instalação em Windows, Linux e macOS](#instalação-em-windows-linux-e-macos)
4. [Tutorial da interface](#tutorial-da-interface)
5. [CLI: comandos completos](#cli-comandos-completos)
6. [Servidor MCP](#servidor-mcp)
7. [GPU, CPU e RAM](#gpu-cpu-e-ram)
8. [Arquivos, segurança e privacidade](#arquivos-segurança-e-privacidade)
9. [Compilação e distribuição](#compilação-e-distribuição)
10. [Testes e limitações](#testes-e-limitações)
11. [Contribuições, versões e licença](#contribuições-versões-e-licença)

## O que é e o que não é

O **Markveil** é uma ferramenta de código aberto, local-first, para fotógrafos que precisam apresentar uma amostra de sua fotografia antes da venda. O programa lê os originais, reduz a resolução e produz **JPEGs marcados em um diretório diferente**. O produto licenciado e em alta resolução permanece separado para entrega pelo fluxo comercial escolhido pelo fotógrafo.

**Não faz:** impedir screenshots; impedir toda remoção de marca d'água; integrar automaticamente plataformas de terceiros; guardar fotos em nuvem; administrar pagamentos. **Adversarial** é uma função experimental separada, não a garantia central do sistema.

## Funcionalidades

| Área | Disponível | Observações |
|---|---|---|
| Desktop | Sim | Interface Tkinter, maximização conforme sistema, antes/depois, presets |
| Marca textual | Sim | Texto, opacidade, repetição e grade |
| Marca PNG | Sim | Logo PNG transparente, repetido na prévia |
| Perfis | Sim | `classic`, `adaptive`, `strong` — intensidade visual, não certificação contra IA |
| Lotes | Sim | Pasta de origem → pasta de saída separada |
| Arrastar e soltar | Opcional | Depende de `tkinterdnd2` e suporte gráfico; mantenha botão de seleção como alternativa |
| Monitoramento | Parcial | CPU/RAM via `psutil`; NVIDIA via `nvidia-smi`, quando disponível |
| CLI | Sim | Processamento, comparação e relatórios |
| MCP | Sim | `stdio`, quatro ferramentas locais |
| Gallery Lab | Sim | Recompressão JPEG e redimensionamento; **não é ataque de IA** |
| Attack Lab | Sim, opcional | Inpainting clássico OpenCV ou comparação com imagem de IA externa |
| Adversarial | Experimental | Exige grandes bibliotecas/modelos; sem resistência comprovada |
| Instaladores assinados | Não | Builds nativos devem ser executados e validados em cada SO |

## Instalação em Windows, Linux e macOS

**Requisitos:** Python **3.10+**, espaço para dependências, acesso ao terminal. Desktop requer ambiente gráfico e Tk/Tcl. MCP/CLI podem funcionar sem tela. Use um ambiente virtual para não afetar Python do sistema.

### Windows 10/11

1. Baixe o ZIP do repositório e extraia, por exemplo, em `C:\Markveil`.
2. Com Python instalado e habilitado, dê dois cliques em `iniciar_windows.bat`.
3. Se preferir comandos manuais, abra PowerShell na pasta:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[desktop]"
.venv\Scripts\python.exe -m markveil.gui
```

> O script Windows foi ajustado para instalar dentro de `.venv`. Caso o Windows bloqueie o script baixado, extraia em pasta própria e confira a procedência antes de executar.

### Linux (Ubuntu/Debian e similares)

Em Ubuntu/Debian, instale Python com `venv` e Tk se ainda não estiverem disponíveis:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk
chmod +x iniciar_linux.sh
./iniciar_linux.sh
```

Outras distribuições usam pacotes equivalentes. Em servidores sem interface gráfica, instale apenas o núcleo/CLI e MCP.

### macOS (Intel e Apple Silicon)

Tenha Python 3.10+ e Tk compatível com a distribuição de Python. No Terminal, dentro da pasta:

```bash
chmod +x iniciar_macos.command
./iniciar_macos.command
```

Ou manualmente:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[desktop]'
python -m markveil.gui
```

O `.app` gerado localmente **não é automaticamente assinado nem notarizado**. macOS poderá exibir alertas do Gatekeeper. Não recomendamos ignorar avisos para programas cuja origem você desconhece.

### Instalação apenas da CLI

```bash
python -m pip install -e .
python -m markveil --help
```

## Tutorial da interface

1. Abra **Estúdio/Proteger** e selecione a pasta das fotos (ou use o arrastar e soltar quando habilitado).
2. Carregue as imagens e selecione uma foto na lista para inspecionar.
3. Configure a marca textual ou o PNG (se desejar), perfil, opacidade, densidade, resolução e qualidade.
4. Clique em **Atualizar prévia** e compare com o original usando o controle deslizante.
5. Selecione **pasta de saída diferente** da pasta de originais.
6. Execute o processamento de todas as fotografias e acompanhe a fila/progresso.
7. Inspecione os JPEGs exportados antes de publicá-los na galeria.
8. Salve um **preset** para repetir a configuração em outras sessões.

O modo maximizado usa mecanismos diferentes por SO. Se a tela for pequena, reduza a escala do sistema ou redimensione a janela; a responsividade ainda necessita testes adicionais.

## CLI: comandos completos

Todos os exemplos abaixo pressupõem o ambiente virtual ativado e o comando `markveil` disponível; alternativa universal: `python -m markveil`.

**Processar lote** (comando principal e seu alias `protect`):

```bash
markveil protect ./originais ./previas --protection strong --text "PRÉVIA - NÃO COMPRADA"
markveil ./originais ./previas --protection adaptive --size 1100 --quality 76
```

**Parâmetros:** `--text` (até 120 caracteres), `--size` (320–3000), `--opacity` (30–240), `--density` (2–9), `--quality` (40–95), `--logo` (PNG), `--logo-scale` (10–65), `--protection classic|adaptive|strong`, `--no-grid`. Use `markveil --help` para ver os valores disponíveis.

**Comparar os três perfis:**

```bash
markveil compare ./originais/foto.jpg ./relatorios/perfis.jpg
```

**Simular alterações das galerias** (não é teste de remoção por IA):

```bash
markveil gallery-test ./originais/foto.jpg ./relatorios/galeria --protection strong
markveil benchmark ./originais/foto.jpg ./relatorios/benchmark
```

**Avaliar imagem tratada externamente por IA:**

```bash
markveil attack-test ./originais/foto.jpg ./relatorios/ataque --attacked ./amostras/removida.jpg
```

**Inpainting clássico local** (depende da extra `attack`, não é IA generativa):

```bash
python -m pip install -e '.[attack]'
markveil attack-test ./originais/foto.jpg ./relatorios/ataque-local --local-inpaint
```

**Outros comandos:**

```bash
markveil gui
markveil version
markveil mcp
```

Saídas dos laboratórios incluem imagens e relatórios HTML/JSON conforme cada módulo. Inspecione a pasta gerada. **Nunca selecione os originais como destino.**

## Servidor MCP

MCP permite que clientes compatíveis solicitem ferramentas locais via **standard input/output (`stdio`)**. Não é um serviço HTTP público e não requer chave paga.

```bash
python -m pip install -e '.[mcp]'
markveil mcp
```

**Ferramentas:** `preview_file(source, destination, text, protection, size, logo)`, `preview_folder(...)`, `compare_file(source, destination)` e `test_gallery(source, destination, protection)`. O cliente deve usar o executável **Python do mesmo ambiente virtual** que contém Markveil e MCP. Exemplos e cuidados: [docs/MCP.md](docs/MCP.md).

> **Segurança:** o MCP pode ler e gravar arquivos indicados pelo cliente. Conecte somente assistentes/clientes confiáveis, sem conceder acesso a pastas sensíveis. A versão atual não implementa sandbox de diretórios.

## GPU, CPU e RAM

A marca d'água convencional usa predominantemente **CPU**. A RAM depende do tamanho e quantidade das imagens. A telemetria pode mostrar uso do computador e consumo do processo; **uso da GPU NVIDIA obtido por `nvidia-smi` é global, não atribuível exclusivamente ao Markveil**. AMD/Intel GPU e Apple Metal/MPS não possuem monitor universal validado nesta versão. A proteção adversarial é opcional e pode demandar GPU compatível, PyTorch e download de modelos grandes. Consulte [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Arquivos, segurança e privacidade

- Processamento local: fotografias **não são enviadas para servidor pelo motor convencional**.
- Arquivos de prévia são **JPEGs separados**; originais não devem ser alterados. Ainda assim, mantenha backups.
- A CLI e o MCP aceitam caminhos definidos pelo usuário; use-os com atenção.
- Presets persistem em `%APPDATA%\Markveil` (Windows), `~/Library/Application Support/Markveil` (macOS) ou `$XDG_CONFIG_HOME/markveil`/`~/.config/markveil` (Linux). Variável `MARKVEIL_CONFIG_DIR` personaliza o local.
- O módulo adversarial opcional pode baixar pesos de modelos de fornecedores externos; verifique termos e conectividade antes do uso.
- Marcas podem ser removidas ou a imagem pode ser reconstruída por IA. Evite expressões como “90% garantido” sem experimento replicável.

## Compilação e distribuição

Os scripts `build_windows.bat`, `build_linux.sh` e `build_macos.sh` utilizam PyInstaller; cada sistema deve produzir seu próprio binário. O workflow CI pode construir artefatos, mas **não cria automaticamente instaladores assinados, `.dmg`, `.deb` ou `.msi`**. Veja o guia detalhado [docs/RELEASING.md](docs/RELEASING.md).

## Testes e limitações

```bash
python -m pip install -e '.[desktop,mcp]' pytest
python -m pytest -q
python -m markveil --help
```

Workflow: `.github/workflows/tests.yml`, com matriz Windows, macOS, Linux. **CI executada de verdade somente após publicar e rodar no GitHub**. Teste manual da UI, arrastar-e-soltar, integração MCP com cliente real, e builds nativos ainda exigem validação.

Problemas frequentes: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Contribuições, versões e licença

- Licença [MIT](LICENSE) e histórico [CHANGELOG.md](CHANGELOG.md).
- Leia [CONTRIBUTING.md](CONTRIBUTING.md) e [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- Reporte bugs usando os modelos em `.github/ISSUE_TEMPLATE/`.
- Processo de releases e convenções de versões: [docs/RELEASING.md](docs/RELEASING.md).
- **Independência:** Markveil não é afiliado ao projeto acadêmico PhotoGuard do MadryLab.
