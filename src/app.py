import sys
from agents.csv_agent import CsvAgent

def prompt_user(csv_agent):
    try:
        while True:
            query = input('Please enter your query about the CSV files: ')
            response = csv_agent.process_query(query)
            print(response)
    except (KeyboardInterrupt, EOFError):
        print('\nExiting CSV Query Agent.')
        sys.exit(0)

def main():
    print('Welcome to the CSV Query Agent!')
    csv_agent = CsvAgent()
    prompt_user(csv_agent)

if __name__ == '__main__':
    main()
