#!/bin/bash

find . -type f -name "*.mp3" -print0 | while IFS= read -r -d '' file; do
    echo "Processing $file..."
    dir=$(dirname "$file")
    
    if whisper "$file" --model turbo --output_dir "$dir"; then
        echo "Successfully transcribed $file. Deleting original mp3."
        rm "$file"
    else
        echo "Failed to transcribe $file."
    fi
done
