#!/bin/bash

# Find and transcribe all .mp3 files in the current directory and subdirectories
find . -type f -name "*.mp3" -print0 | while IFS= read -r -d '' file
do
    echo "Transcribing: $file"
    
    # Run whisper and output to the same directory
    ~/.local/bin/whisper "$file" --model base --output_dir "$(dirname "$file")"
    
    # Check if the whisper command was successful
    if [ $? -eq 0 ]; then
        rm "$file"
        echo "Deleted original: $file"
    else
        echo "Failed to transcribe: $file, skipping deletion."
    fi
done

echo "Transcription complete!"
