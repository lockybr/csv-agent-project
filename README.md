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

### 4. Modelos Free Disponíveis
A interface permite selecionar entre os seguintes modelos gratuitos do OpenRouter:
- `deepseek/deepseek-prover-v2:free`
- `nousresearch/nous-capybara-7b:free`
- `openchat/openchat-7b:free`

### 5. Inicie o servidor web
Configure o aplicativo Flask e inicie o servidor:
```powershell
$env:FLASK_APP="src/web_app.py"
python -m flask run
```

### Observação sobre encadeamento de comandos
No PowerShell, use `;` para encadear comandos em vez de `&&`. Por exemplo:
```powershell
pip install -r requirements.txt; python -m flask run
```

### 6. Use a interface web
Abra o navegador em http://127.0.0.1:5000/

- Faça upload de arquivos CSV.
- Faça perguntas em linguagem natural sobre os dados.
- A interface agora exibe o modelo selecionado e a pergunta enviada junto com a resposta.

### 7. Limite de Requisições
Os modelos gratuitos possuem um limite de 50 requisições por dia. Caso o limite seja excedido, você verá o seguinte erro:
```
Erro: Error code: 429 - {'error': {'message': 'Rate limit exceeded: free-models-per-day. Add 10 credits to unlock 1000 free model requests per day', 'code': 429, 'metadata': {'headers': {'X-RateLimit-Limit': '50', 'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1748822400000'}, 'provider_name': None}}}
```
Para desbloquear mais requisições, adicione créditos no OpenRouter para aumentar o limite para 1000 requisições por dia.

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