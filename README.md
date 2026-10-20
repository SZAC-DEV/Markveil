# PhotoGuard v0.6 — Módulo adversarial experimental

**Novidade:** módulo opcional de perturbação adversarial de prévias, inspirado conceitualmente na pesquisa [MadryLab/photoguard](https://github.com/madrylab/photoguard). **Não incorpora código deles e NÃO reproduz fielmente seu encoder attack.** Este protótipo maximiza a distância entre representações latentes de um VAE pré-treinado, com perturbação limitada por `epsilon`. Nenhuma alegação de eficácia contra remoção de marcas d’água por IA foi validada.

## Uso no Windows

1. Para as funções normais, execute `iniciar_windows.bat` (continua leve, sem IA).
2. Para a nova opção **PROTEÇÃO ADVERSARIAL EXPERIMENTAL**, instale manualmente em um terminal na pasta do programa:
   `py -3 -m pip install -e ".[adversarial]"`
3. Opcionalmente, instale PyTorch com suporte CUDA seguindo [as instruções oficiais](https://pytorch.org/get-started/locally/). A instalação genérica do pip pode não incluir a versão CUDA adequada. CPU funciona, mas é lenta.
4. Gere uma prévia com marca d'água usando o PhotoGuard. Depois clique no botão experimental e selecione a **prévia**, nunca a foto original.
5. A primeira execução baixa o VAE do Hugging Face; requer internet, armazenamento e respeito à licença do modelo. Depois o processamento é local.

Também é possível usar:

```powershell
py -3 -m photoguard.adversarial "C:\Previas\foto.jpg" "C:\Previas\foto-protegida.png" --epsilon 6 --steps 20 --size 512 --device auto
```

**Limitações relevantes:** a imagem é redimensionada para até 512 pixels e cortada até múltiplos de 8; o resultado é PNG; otimizar contra um VAE não garante transferibilidade contra IAs modernas. Processamento pesado requer GPU ou tempo de CPU. A saída pode ficar pior após compressão/redimensionamento por plataformas comerciais. Nunca envie original ou arquivo já marcado para serviços que exijam o original intacto.

**Para testar resistência real:** execute a ferramenta de remoção de sua escolha sobre as prévias e use o laboratório já existente em `TESTAR RESULTADO DE IA EXTERNA`. Não confunda alteração do embedding com resistência comprovada.

---

## v0.4.2 — correção de inicialização

Corrigido o conflito entre `App._options()` e `tkinter.Tk._options()`, que impedia a abertura da GUI no Python 3.13. Execute `iniciar_windows.bat` no Windows.

**Nota:** esta correção foi validada com testes automatizados e verificação estática; não foi testada com exibição gráfica real em Windows.

# PhotoGuard 🛡️

**Ferramenta open source para gerar prévias fotográficas com marcas d'água reforçadas, sem alterar os originais.**

> **Aviso:** nenhuma marca d'água visível garante proteção contra remoção por IA. A v0.2 utiliza texto distribuído, grades e redução de resolução. Não implementa proteção adversarial validada. Não é uma plataforma de vendas e não contorna políticas de terceiros.

## Funcionalidades (v0.4)
- PNG transparente personalizado repetido na prévia, com escala e opacidade ajustáveis.
- Botão de visualização da primeira foto antes de processar a pasta.
- Interface desktop com Tkinter (Windows/Linux/macOS com Tk disponível).
- Linha de comando para processamento em lote, inclusive subpastas.
- Marca d'água textual repetida e girada, com grade geométrica opcional.
- Exportação JPEG com resolução e compressão configuráveis.
- Arquivos originais preservados; saída obrigatoriamente fora da árvore de entrada.
- Metadados EXIF/GPS não propagados para as prévias.
- Relatório JSON de processamento, hashes SHA-256 dos originais.
- 100% local e sem API paga.

## Instalação
É necessário Python 3.10+ (Windows 10/11 ou Linux).

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -e .
photoguard-gui
```

Se `photoguard-gui` não estiver disponível, execute `python -m photoguard.gui`.

## Linha de comando
```bash
photoguard "C:/Fotos/Originais" "C:/Fotos/Previas" --text "© Meu Estúdio · PRÉVIA" --size 1100 --density 5 --opacity 145 --logo "C:/Fotos/logo.png" --logo-scale 30
```

Detalhes: `photoguard --help`.

## Gerar .exe para Windows
Execute os comandos **no próprio Windows**. Um `.exe` Windows não é gerado diretamente pelo PyInstaller rodando em Linux/Termux.

```powershell
pip install -e . pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name PhotoGuard --collect-all PIL --paths src launcher.py
```

O executável ficará em `dist/PhotoGuard.exe`. O arquivo `launcher.py` já está incluído. Pode exigir validação de antivírus e testes em instalações limpas.

## Compatibilidade com plataformas

| Plataforma | Estado no projeto |
|---|---|
| Fotop | Exportar marca PNG é uma possível integração futura; a v0.2 usa PNG como sobreposição nas prévias, mas **não** gera modelos especiais para envio à plataforma. |
| Banlek | **Não enviar** arquivos já marcados; os termos proíbem e a plataforma aplica sua proteção. Sem integração nesta versão. |
| Fotto | Fluxo externo não integrado; verifique suporte oficial para prévias customizadas. |
| Outros sites | É possível usar as prévias onde o serviço admite imagem de prévia diferente do original; caso contrário, não existe integração automática. |

## Segurança / limites
- O app não gerencia compra, pagamento, autenticação ou entrega de originais.
- Imagens exibidas publicamente podem ser capturadas por screenshot e manipuladas por IA.
- Não coloque originais em diretório público do site; armazene-os de forma privada e entregue somente com autorização.
- Relatório contém caminhos locais e hashes, não deve ser publicado inadvertidamente.
- Recomenda-se manter cópias de segurança dos originais, separadas da pasta de processamento.

## Próximos marcos
- v0.3: templates configuráveis e exportação de marca PNG para plataformas compatíveis.
- v0.3: testes padronizados contra inpainting, remoção por IA e compressão, com métricas antes de alegar resistência.
- v0.4: API local e adaptadores oficiais conforme contratos das plataformas.

## Testes
```bash
pip install -e .
python -m unittest discover -s tests -v
```

## Contribuição e licença
Issues, PRs e testes de campo são bem-vindos. MIT — consulte LICENSE.

## Versão 0.3 — Avaliação local de transformações

O botão **AVALIAR RESISTÊNCIA A COMPRESSÃO (NÃO IA)** escolhe a primeira fotografia da pasta e cria `index.html`, `benchmark.json` e quatro imagens para comparação em uma pasta externa à origem. O relatório mede diferença média de pixels na prévia, após duas compressões JPEG e redução de 50% da resolução. **Não é teste de remoção por IA, não mede se texto continua legível e não comprova resistência adversarial.**

Na linha de comando:

```powershell
photoguard benchmark "C:\Fotos\ensaio.jpg" "C:\Relatorios\ensaio" --text "PRÉVIA NÃO COMPRADA"
```

A pasta de relatório precisa ficar fora da pasta da foto original. Não há upload externo, reconhecimento facial ou conexão com plataformas comerciais. Integração com Fotto, Fotop e Banlek permanece condicionada às APIs e políticas oficiais.

## v0.4 — Laboratório de ataques (experimental)

**Novo:** CLI `attack-test`, botão **TESTAR RESULTADO DE IA EXTERNA** na interface gráfica, e relatório HTML/JSON com prévia, imagem pós-ataque, máscara aproximada e métricas (MAE, PSNR, redução relativa do erro). Permite testar uma imagem produzida manualmente em qualquer ferramenta de IA, sem API paga e sem envio automático de fotos.

```powershell
photoguard attack-test "C:\Fotos\original.jpg" "C:\Relatorios\ataque" --attacked "C:\Fotos\editada_por_ia.png"
```

**Limitação importante:** a edição externa deve ter o mesmo enquadramento; a ferramenta redimensiona para comparar, mas mudanças de corte e conteúdo tornam as métricas pouco úteis. O script cria sua própria prévia marcada antes da comparação: para testar uma remoção real, a imagem fornecida deve ter sido criada a partir da prévia PhotoGuard com as **mesmas opções de marca e tamanho**. Para logotipo, adicione `--logo "C:\Fotos\logo.png"`; o comando usa o tamanho padrão de 1100 px. Para testes rigorosos de ajustes diferentes, exporte a prévia primeiro usando as mesmas opções ou desenvolva um parâmetro para carregar a prévia marcada existente.

Teste opcional com *inpainting clássico* OpenCV (Telea; **não é IA generativa**):

```powershell
pip install -e ".[attack]"
photoguard attack-test "C:\Fotos\original.jpg" "C:\Relatorios\inpaint" --local-inpaint
```

A máscara é inferida por diferença dos pixels entre prévia e original reduzido. Ela é imprecisa devido à compressão e outras alterações; uma máscara branca-preto real pode ser fornecida com `--mask`. Não há pesos de IA, métricas de legibilidade de logo, classificação de proteção, integração com sites de venda ou promessa de impedir remoção. Testar somente imagens próprias ou autorizadas.

## Windows - iniciar com duplo clique

Depois de extrair o ZIP, abra a pasta `PhotoGuard` e clique em `iniciar_windows.bat`.
Este script verifica a disponibilidade do Python, instala dependencias e abre a interface.
Se houver um erro, o terminal permanece aberto para permitir que voce copie a mensagem.
Para compilar, use `build_windows.bat` (gera `dist/PhotoGuard.exe` no Windows).

Para executar testes diretamente do repositorio (sem instalacao editavel), use `py -m pip install pytest` e `py -m pytest -q`.


## v0.5.0 — Perfis de proteção visual

Novo controle **Perfil de proteção** na interface e `--protection classic|adaptive|strong` na CLI.

- `classic`: marca textual/PNG repetida + grade opcional (comportamento anterior).
- `adaptive` (padrão): adiciona pequenos traços contrastantes conforme a luminosidade local.
- `strong`: maior densidade de traços e cruzes sobre a imagem.

Os perfis adicionam **obstrução visual** às prévias. **Não são perturbações adversariais verificadas**, nem impedem a reconstrução por modelos generativos. O teste de compressão existente não mede proteção contra IA. Use a imagem original exclusivamente na entrega após pagamento e apenas prévias reduzidas para divulgação.

### Exemplo de uso

`photoguard "C:\Fotos" "C:\Previas" --protection strong --size 1100`


### Comparar perfis lado a lado
Na interface, clique em **COMPARAR 3 PERFIS**. Uma montagem JPEG é salva com os perfis clássico, adaptativo e forte. Também disponível pelo terminal: `photoguard compare foto.jpg comparacao.jpg`.
