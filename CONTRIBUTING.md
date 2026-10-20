# Contribuindo com o Markveil

Obrigado por contribuir. Priorize correções reproduzíveis, documentação clara e funcionalidades que não alterem os originais.

## Preparação

```bash
python -m venv .venv
# ative a venv conforme seu sistema
python -m pip install -e '.[desktop,mcp,attack]' pytest
python -m pytest -q
```

1. Abra uma issue descrevendo o problema ou funcionalidade.
2. Crie branch para a alteração e mantenha mudanças focadas.
3. Escreva testes para bugs e recursos novos; rode CI localmente quando possível.
4. Atualize documentação e CHANGELOG quando alterar comportamento público.
5. Abra pull request com SO testado, prints da interface (sem fotos privadas), escopo e limitações.

**Regras técnicas:** evite operações destrutivas sobre arquivos originais; não introduza APIs pagas obrigatórias; não exponha arquivos locais pelo MCP sem revisar autorização; não afirme resistência quantitativa contra IA sem benchmark reproduzível.

Leia [arquitetura](docs/ARCHITECTURE.md), [releases](docs/RELEASING.md) e [código de conduta](CODE_OF_CONDUCT.md).
