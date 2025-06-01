import os
import zipfile

def unpack_archives(data_dir):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    for file in os.listdir(data_dir):
        if file.endswith('.zip'):
            with zipfile.ZipFile(os.path.join(data_dir, file), 'r') as zip_ref:
                zip_ref.extractall(data_dir)
