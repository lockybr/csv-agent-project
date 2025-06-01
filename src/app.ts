import { CsvAgent } from './agents/csvAgent';
import * as readline from 'readline';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const csvAgent = new CsvAgent();

const promptUser = () => {
    rl.question('Please enter your query about the CSV files: ', async (query) => {
        const response = await csvAgent.processQuery(query);
        console.log(response);
        promptUser();
    });
};

const initApp = () => {
    console.log('Welcome to the CSV Query Agent!');
    promptUser();
};

initApp();