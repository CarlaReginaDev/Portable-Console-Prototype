#!/bin/bash

# Simple script to decompress downloaded archives based on their extension

# Check if a file was provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <archive-file>"
    echo "Supported formats: .gz .bz2 .xz .zip .tar .tar.gz .tar.bz2 .tar.xz"
    exit 1
fi

FILE="$1"

# Check if file exists
if [ ! -f "$FILE" ]; then
    echo "Error: File '$FILE' not found"
    exit 1
fi

# Get the file extension
filename=$(basename -- "$FILE")
extension="${filename##*.}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Decompress based on extension
case "$filename" in
    *.tar.gz|*.tgz)
        echo "Decompressing tar.gz file..."
        tar -xzf "$FILE"
        ;;
    *.tar.bz2|*.tbz2)
        echo "Decompressing tar.bz2 file..."
        tar -xjf "$FILE"
        ;;
    *.tar.xz|*.txz)
        echo "Decompressing tar.xz file..."
        tar -xJf "$FILE"
        ;;
    *.gz)
        echo "Decompressing gzip file..."
        if command_exists "pigz"; then
            pigz -dk "$FILE"
        else
            gzip -dk "$FILE"
        fi
        ;;
    *.bz2)
        echo "Decompressing bzip2 file..."
        bzip2 -dk "$FILE"
        ;;
    *.xz)
        echo "Decompressing xz file..."
        xz -dk "$FILE"
        ;;
    *.zip)
        echo "Decompressing zip file..."
        unzip "$FILE"
        ;;
    *.tar)
        echo "Decompressing tar file..."
        tar -xf "$FILE"
        ;;
    *)
        echo "Error: Unknown or unsupported file format for '$FILE'"
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    echo "Decompression successful!"
else
    echo "Decompression failed!"
fi

