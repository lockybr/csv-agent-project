Esse é um agente criado para cumprir os desafios de caráter eliminatório propostos pelo curso I2A2

Objetivo:
• Criar um ou mais agentes que tornem possível a um usuário realizar perguntas sobre os arquivos CSV disponibilizados.
• Exemplo: Qual é o fornecedor que teve maior montante recebido? Qual item teve maior volume entregue (em quantidade)? E assim por diante.

Modo de operação:
• Interface onde o usuário informa sua pergunta. O agente gera a resposta.
• O(s) agente(s) deverá:
  • selecionar o arquivo desejado
  • carregar os dados
  • fazer as queries
  • gerar a resposta para o usuário.

# CSV Query Agent (Python + LangChain + Flask)

Este projeto permite que você faça perguntas em linguagem natural sobre arquivos CSV enviados, usando uma interface web simples e inteligência artificial (LangChain + OpenRouter).

## Como rodar o projeto

### 1. Clone o repositório
```powershell
git clone <URL_DO_SEU_REPOSITORIO>
cd csv-agent-project
```

### 2. Instale as dependências
```powershell
pip install -r requirements.txt
```

### 3. Configure sua chave da OpenRouter
Obtenha uma chave gratuita em https://openrouter.ai/

No PowerShell, rode:
```powershell
$env:OPENAI_API_KEY="sua-chave-openrouter"
$env:OPENAI_API_BASE="https://openrouter.ai/api/v1"
```

### 4. Inicie o servidor web
```powershell
python src/web_app.py
```

### 5. Use a interface web
Abra o navegador em http://127.0.0.1:5000/

- Faça upload de arquivos CSV.
- Faça perguntas em linguagem natural sobre os dados.

## Estrutura do projeto
- `src/web_app.py`: Interface web Flask.
- `src/agents/csv_agent.py`: Lógica do agente inteligente.
- `src/data/`: Coloque seus arquivos CSV aqui.

## Observações
- O projeto já inclui exemplos de CSV em `src/data/`.
- O processamento depende de conexão com a internet para acessar o LLM via OpenRouter.
- Para dúvidas ou melhorias, abra uma issue ou pull request!

---

**Pronto para ser clonado, rodado e avaliado!**