import { loadData } from '../utils/dataLoader';
import { executeQuery } from '../utils/queryExecutor';
import { generateResponse } from '../responses/responseGenerator';
import { Query } from '../types';

export class CsvAgent {
    private data: any;

    constructor() {
        this.data = null;
    }

    public async processQuery(query: Query): Promise<string> {
        if (!this.data) {
            throw new Error("No data loaded. Please load a CSV file first.");
        }

        const results = executeQuery(this.data, query);
        return generateResponse(results);
    }

    public async loadCsvData(filePath: string): Promise<void> {
        this.data = await loadData(filePath);
    }
}