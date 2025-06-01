import * as fs from 'fs';
import * as path from 'path';
import * as unzipper from 'unzipper';

export const unpackFiles = async (filePath: string, outputDir: string): Promise<void> => {
    return new Promise((resolve, reject) => {
        fs.createReadStream(filePath)
            .pipe(unzipper.Extract({ path: outputDir }))
            .on('close', resolve)
            .on('error', reject);
    });
};