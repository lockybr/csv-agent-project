import os
import zipfile
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

class CsvAgent:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self._unpack_archives()

    def _unpack_archives(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        for file in os.listdir(self.data_dir):
            if file.endswith('.zip'):
                with zipfile.ZipFile(os.path.join(self.data_dir, file), 'r') as zip_ref:
                    zip_ref.extractall(self.data_dir)

    def process_query(self, query, model, api_key):
        # Se o usuário informar a key no campo, usa ela. Caso contrário, recupera do ambiente.
        effective_api_key = api_key.strip() if api_key else os.environ.get('OPENROUTER_API_KEY')

        if not effective_api_key:
            return "Erro: Nenhuma API key válida foi fornecida. (OPENROUTER_API_KEY não encontrada no ambiente e não foi informada no formulário)"

        try:
            chat = ChatOpenAI(
                streaming=True,
                callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
                model_name=model,
                temperature=0,
                openai_api_key=effective_api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                max_tokens=1500
            )
        except Exception as e:
            return f"Erro ao inicializar o modelo: {str(e)}"

        responses = []
        # Só exibe a API key (parcial) se o usuário NÃO informar nada no campo
        if not api_key and effective_api_key:
            key_display = effective_api_key[:4] + "..." + effective_api_key[-4:]
            responses.append(f"[OS_ENV_KEY] Usando API key do ambiente: {key_display}")

        for file in os.listdir(self.data_dir):
            if file.endswith('.csv'):
                try:
                    with open(os.path.join(self.data_dir, file), 'r', encoding='latin1') as f:
                        csv_content = f.read()

                    message = HumanMessage(content=f"""
                    Analise os dados do arquivo CSV abaixo e responda à pergunta: {query}

                    Dados do arquivo {file}:
                    {csv_content}

                    Observação: 
                    - Os aruivos que terminam com _Cabecalho.csv ou NotaFiscal.csv contêm o valor total da nota. Os arquivos que terminam com Item.csv contêm todos os itens/detahes que compõem a nota.
                    - Use formatação adequada para valores monetários (R$ com ponto para milhares e vírgula para decimais)
                    - Se não for possível responder com os dados disponíveis, indique isso claramente
                    """)

                    result = chat.invoke([message])
                    responses.append(f"Arquivo: {file}\nResposta: {result.content}")

                except Exception as e:
                    msg = str(e)
                    if '401' in msg or 'No auth credentials' in msg:
                        responses.append(f"Arquivo: {file}\nErro: Falha de autenticação. Verifique se sua API key do OpenRouter está correta e ativa.")
                        break
                    elif '429' in msg:
                        responses.append(f"Arquivo: {file}\nErro: Limite de requisições atingido. Tente novamente mais tarde ou adicione créditos ao OpenRouter.")
                        break
                    else:
                        responses.append(f"Arquivo: {file}\nErro: Não foi possível processar a resposta. Detalhes: {msg}")
        return "\n\n".join(responses)
