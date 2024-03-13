import os
import hashlib

def hash_folder(folder_path):
    sha256 = hashlib.sha256()

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Exclude files with the .py extension and the script file itself
            if not file_path.endswith(".py") and file_path != os.path.abspath(__file__):
                with open(file_path, "rb") as f:
                    # Read the file in chunks to avoid memory issues with large files
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)

    return sha256.hexdigest()

# Example usage
folder_path = "."
hashed_value = hash_folder(folder_path)
print(hashed_value)#