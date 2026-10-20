# Publicação de releases — Markveil

Este guia separa **código-fonte**, **artefatos de CI** e **instaladores para usuários**. Até uma versão ser validada, rotule como `Pre-release` no GitHub.

## SemVer e checklist

- Para a beta atual, use `v0.13.0`; próximas mudanças seguem `vMAJOR.MINOR.PATCH`.
- Atualize `pyproject.toml`, `CHANGELOG.md`, README e testes.
- Execute `python -m pytest -q` e `python -m markveil --help`.
- Teste fluxo real de proteção com arquivos temporários e verifique que originais não mudaram.
- Teste GUI em Windows 10/11, Ubuntu e macOS, inclusive arrastar/soltar, presets, slides e layout em 1366×768 e 1920×1080.
- Verifique licença de todas as dependências e imagens de screenshots; elimine dados pessoais.
- Revise os riscos do MCP e a qualidade da documentação.

## GitHub Actions

`.github/workflows/tests.yml` roda testes em Windows, Linux, macOS e permite compilação manual com **Actions → Cross-platform tests → Run workflow**. Builds são enviados como **Actions artifacts**, não como uma release pública automática. Baixe e teste os artefatos.

## Compilação local

**Windows:** execute `build_windows.bat` no Windows. O script utiliza PyInstaller. Resultado previsto: `dist/Markveil.exe`, mas não é um instalador MSI. 

**Linux:** `bash build_linux.sh` na distro-alvo. Resultado previsto: `dist/Markveil/`. Empacote a pasta para distribuição e informe bibliotecas gráficas necessárias. Não chame o arquivo de AppImage ou `.deb` sem construir esses formatos.

**macOS:** `bash build_macos.sh` em macOS. Resultado previsto: `dist/Markveil.app` sem assinatura/notarização. Produza builds nativos para arquiteturas necessárias, assine/notarize segundo as regras da Apple e teste numa máquina limpa antes de disponibilizar um `.dmg`.

> Atenção: distribuição sem assinatura pode provocar bloqueios e alertas de segurança. Não incentive usuários a desativar proteções do SO.

## Criar release manual no GitHub

1. Publique o repositório.
2. Confirme que os testes passaram nos três sistemas.
3. Crie uma tag `v0.13.0` a partir do commit revisado.
4. GitHub → **Releases → Draft a new release**; selecione a tag.
5. Marque **Pre-release** (beta).
6. Anexe os builds realmente testados, suas somas SHA-256 e o ZIP de código-fonte, se necessário.
7. Escreva notas com funcionalidades, requisitos, bugs conhecidos, mudança de configuração e aviso sobre IA.
8. Após publicar, instale a partir dos artefatos de release e execute o fluxo de teste mais uma vez.

## Modelo de notas

```markdown
## Markveil v0.13.0 (Beta)
- Documentação unificada e guias por plataforma
- Motor de prévias/CLI/MCP preservados
### Instalação
- Windows: script de origem / build verificado (se disponível)
- Linux: script de origem / build verificado (se disponível)
- macOS: script de origem / .app testado (se disponível)
### Limitações
- Sem garantia de resistência contra IA
- Distribuições não assinadas/notarizadas se aplicável
### Segurança
- MCP com acesso local a arquivos: use clientes confiáveis
```

## Publicação no PyPI

**Ainda não feita.** Antes de executar `twine upload`, confirme disponibilidade de nome, ownership, licença de terceiros, metadados, pacote wheel/sdist e testes de instalação em ambiente limpo. `pip install markveil` não deve ser anunciado enquanto publicação real não existir.
