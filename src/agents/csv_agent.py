import os
import zipfile
import pandas as pd
from langchain_openai import OpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

class CsvAgent:
    def __init__(self):
        self.dataframes = {}
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self._unpack_archives()
        self._load_csvs()
        self.llm = OpenAI(
            temperature=0,
            openai_api_key=os.environ.get('OPENAI_API_KEY'),
            openai_api_base=os.environ.get('OPENAI_API_BASE'),
        )
        self.agents = {}
        for file, df in self.dataframes.items():
            self.agents[file] = create_pandas_dataframe_agent(
                self.llm, df, verbose=False, allow_dangerous_code=True, handle_parsing_errors=True
            )

    def _unpack_archives(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        for file in os.listdir(self.data_dir):
            if file.endswith('.zip'):
                with zipfile.ZipFile(os.path.join(self.data_dir, file), 'r') as zip_ref:
                    zip_ref.extractall(self.data_dir)

    def _load_csvs(self):
        for file in os.listdir(self.data_dir):
            if file.endswith('.csv'):
                # Load full dataframe without sampling
                try:
                    df = pd.read_csv(os.path.join(self.data_dir, file), encoding='latin1', on_bad_lines='skip')
                    self.dataframes[file] = df
                except (UnicodeDecodeError, pd.errors.ParserError) as e:
                    print(f"Erro ao carregar {file}: {e}")

    def process_query(self, query, model=None):
        # Create a new instance of OpenAI with the selected model
        llm = OpenAI(
            temperature=0,
            openai_api_key=os.environ.get('OPENAI_API_KEY'),
            openai_api_base=os.environ.get('OPENAI_API_BASE'),
            model=model
        )
        # Try to answer using all loaded CSVs
        responses = []
        for file, agent in self.agents.items():
            try:
                answer = agent.invoke({"input": query}, llm=llm)
                responses.append(f"Arquivo: {file}\nResposta: {answer['output']}")
            except Exception as e:
                responses.append(f"Arquivo: {file}\nErro: {str(e)}")
        return "\n\n".join(responses)
