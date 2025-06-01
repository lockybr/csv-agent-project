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
            model="deepseek/deepseek-prover-v2:free"  # Reverting to a previously working free model
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
                df = pd.read_csv(os.path.join(self.data_dir, file))
                self.dataframes[file] = df

    def process_query(self, query):
        # Try to answer using all loaded CSVs
        responses = []
        for file, agent in self.agents.items():
            try:
                answer = agent.invoke({"input": query})
                responses.append(f"Arquivo: {file}\nResposta: {answer['output']}")
            except Exception as e:
                responses.append(f"Arquivo: {file}\nErro: {str(e)}")
        return "\n\n".join(responses)
