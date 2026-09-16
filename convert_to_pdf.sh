#!/bin/bash

# Check if LibreOffice is installed
if ! command -v libreoffice &> /dev/null
then
    echo "Error: libreoffice is not installed. Please install it to use this script."
    echo "You can typically install it using: sudo apt install libreoffice"
    exit 1
fi

# Find and convert all .docx, .pptx, and .xlsx files in the current directory and subdirectories
find . -type f \( -name "*.docx" -o -name "*.pptx" -o -name "*.xlsx" \) -print0 | while IFS= read -r -d '' file
do
    echo "Converting: $file"
    libreoffice --headless --convert-to pdf "$file" --outdir "$(dirname "$file")"
    
    # Verify the PDF was created before deleting the original
    pdf_file="${file%.*}.pdf"
    if [ -f "$pdf_file" ]; then
        rm "$file"
        echo "Deleted original: $file"
    else
        echo "Failed to convert: $file (PDF not found), skipping deletion."
    fi
done

echo "Conversion complete!"
