# Servidor MCP — guia

O servidor usa o SDK Python `mcp` e transporte `stdio`. Instale `python -m pip install -e ".[mcp]"` num ambiente virtual.

## Inicialização

```bash
python -m markveil.mcp_server
# ou: markveil mcp
```

## Exemplo de configuração do cliente

Substitua `CAMINHO_ABSOLUTO_PYTHON` pelo interpretador do ambiente virtual, como `C:\\Markveil\\.venv\\Scripts\\python.exe` (Windows) ou `/home/user/Markveil/.venv/bin/python` (Linux); em macOS use o caminho `.venv/bin/python` correspondente.

```json
{
  "mcpServers": {
    "markveil": {
      "command": "CAMINHO_ABSOLUTO_PYTHON",
      "args": ["-m", "markveil.mcp_server"]
    }
  }
}
```

O nome da chave de configuração pode variar conforme o cliente MCP. Não use Python de outro ambiente: ele pode não encontrar o módulo.

## Ferramentas disponibilizadas

| Ferramenta | Parâmetros essenciais | Saída |
|---|---|---|
| `preview_file` | `source` (foto), `destination` (arquivo `.jpg`), `text`, `protection`, `size`, `logo` | Dados sobre a prévia |
| `preview_folder` | `source` (pasta), `destination` (pasta separada), demais configurações | Resumo do lote |
| `compare_file` | `source` (foto), `destination` (arquivo destino) | Caminho da comparação |
| `test_gallery` | `source` (foto), `destination` (pasta de relatórios), `protection` | Relatório |

Apenas `classic`, `adaptive` e `strong` são perfis convencionais válidos. A CLI dispõe de funcionalidades adicionais não expostas pelo MCP.

## Modelo de segurança

O MCP tem capacidade de acessar os arquivos para os quais o usuário/cliente aponta, sob as permissões do processo que o iniciou. **Não há lista restritiva de diretórios, autenticação, confirmação por operação ou isolamento de filesystem nesta versão.** Não exponha o transporte pela internet, nem conecte clientes não confiáveis. Evite acessar fotos confidenciais com assistentes de terceiros.

## Diagnóstico

Execute `python -m markveil.mcp_server` e confira se o processo permanece ativo aguardando mensagens. Para testes reais, use um cliente MCP compatível; iniciar o servidor sozinho não comprova a integração.
