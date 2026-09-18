import os
import shutil
from pathlib import Path

def main():
    source_dirs = ['MIL1', 'MIL2', 'MIL3', 'MIL4']
    target_dir = Path('Files')
    hierarchy_file = Path('heirarchy.txt')

    # Create the target directory
    target_dir.mkdir(exist_ok=True)

    # Open the hierarchy file for writing
    with open(hierarchy_file, 'w', encoding='utf-8') as hf:
        hf.write("Original Path -> Copied Filename\n")
        hf.write("-" * 40 + "\n")
        
        for d in source_dirs:
            dir_path = Path(d)
            if not dir_path.is_dir():
                print(f"Warning: Directory '{d}' not found.")
                continue

            # Walk through the directory and its subdirectories
            for root, _, files in os.walk(dir_path):
                for filename in files:
                    source_path = Path(root) / filename
                    
                    # Generate a unique filename for the target directory to avoid overwriting files with the same name
                    target_path = target_dir / filename
                    counter = 1
                    while target_path.exists():
                        target_path = target_dir / f"{source_path.stem}_{counter}{source_path.suffix}"
                        counter += 1
                    
                    try:
                        # Copy the file to the Files directory
                        shutil.copy2(source_path, target_path)
                        # Document its original position and new name
                        hf.write(f"{source_path} -> {target_path.name}\n")
                    except Exception as e:
                        print(f"Error copying {source_path}: {e}")

    print(f"Files have been consolidated into the '{target_dir}' directory.")
    print(f"The hierarchy has been documented in '{hierarchy_file}'.")

if __name__ == '__main__':
    main()
