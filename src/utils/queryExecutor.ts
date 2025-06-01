export function executeQuery(data: any[], query: string): any[] {
    // Simple query execution logic
    const results = data.filter(row => {
        return Object.values(row).some(value => 
            String(value).toLowerCase().includes(query.toLowerCase())
        );
    });
    return results;
}