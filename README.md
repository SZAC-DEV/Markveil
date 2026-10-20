# PhotoGuard 🛡️

**Ferramenta open source para gerar prévias fotográficas com marcas d'água reforçadas, sem alterar os originais.**

> **Aviso:** nenhuma marca d'água visível garante proteção contra remoção por IA. A v0.1 utiliza texto distribuído, grades e redução de resolução. Não implementa proteção adversarial validada. Não é uma plataforma de vendas e não contorna políticas de terceiros.

## Funcionalidades (v0.1)
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
photoguard "C:/Fotos/Originais" "C:/Fotos/Previas" --text "© Meu Estúdio · PRÉVIA" --size 1100 --density 5 --opacity 145
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
| Fotop | Exportar marca PNG é uma possível integração futura; a v0.1 **não** gera PNG de marca para envio à plataforma. |
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
- v0.2: marcas d'água PNG personalizadas, templates configuráveis e exportação de marca PNG para plataformas compatíveis.
- v0.3: testes padronizados contra inpainting, remoção por IA e compressão, com métricas antes de alegar resistência.
- v0.4: API local e adaptadores oficiais conforme contratos das plataformas.

## Testes
```bash
pip install -e .
python -m unittest discover -s tests -v
```

## Contribuição e licença
Issues, PRs e testes de campo são bem-vindos. MIT — consulte LICENSE.
