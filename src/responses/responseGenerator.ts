export function generateResponse(results: any, query: string): string {
    if (!results || results.length === 0) {
        return `No results found for your query: "${query}".`;
    }

    const formattedResults = results.map((result: any) => {
        return JSON.stringify(result, null, 2);
    }).join('\n');

    return `Here are the results for your query: "${query}":\n${formattedResults}`;
}