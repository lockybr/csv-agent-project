export interface Query {
    id: number;
    text: string;
}

export interface Response {
    queryId: number;
    results: any[];
    message: string;
}