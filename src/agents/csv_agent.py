import os
os.environ['OPENAI_API_KEY'] = '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'
import zipfile
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.chat_models import ChatOpenAI
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
        effective_api_key = api_key if api_key else os.environ.get('OPENAI_API_KEY')

        if not effective_api_key:
            raise ValueError("No valid API key provided.")

        chat = ChatOpenAI(
            streaming=True,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            model_name=model,
            temperature=0,
            openai_api_key=effective_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            max_tokens=1500
        )

        responses = []
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
                    print(f"Error processing file {file}: {str(e)}")
                    responses.append(f"Arquivo: {file}\nErro: Não foi possível processar a resposta. Detalhes: {str(e)}")
        
        return "\n\n".join(responses)
