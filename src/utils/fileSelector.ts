export function selectFile(files: string[]): string | null {
    if (files.length === 0) {
        console.error("No files available to select.");
        return null;
    }

    // For simplicity, we will just return the first file in the list.
    // In a real application, you might want to implement a more sophisticated selection mechanism.
    return files[0];
}