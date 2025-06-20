#!/bin/bash

# Directory where archives are stored (e.g., ~/Downloads)
DOWNLOADS_DIR="Downloads/"
EXTRACT_DIR="$DOWNLOADS_DIR/extracted"

# Create extraction directory if it doesn't exist
mkdir -p "$EXTRACT_DIR"

# Check if file was provided
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

# Get filename without full path
FILENAME=$(basename -- "$FILE")

# Function to run a command and capture output/status
run_command() {
    local cmd="$@"
    local output
    output=$(eval "$cmd" 2>&1)
    local status=$?
    echo "$output"
    return $status
}

# Decompress based on file type
case "$FILENAME" in
    *.tar.gz|*.tgz)
        echo "Extracting $FILENAME (tar.gz)..."
        OUTPUT=$(run_command "tar -xzf \"$FILE\" -C \"$EXTRACT_DIR\"")
        ;;
    *.tar.bz2|*.tbz2)
        echo "Extracting $FILENAME (tar.bz2)..."
        OUTPUT=$(run_command "tar -xjf \"$FILE\" -C \"$EXTRACT_DIR\"")
        ;;
    *.tar.xz|*.txz)
        echo "Extracting $FILENAME (tar.xz)..."
        OUTPUT=$(run_command "tar -xJf \"$FILE\" -C \"$EXTRACT_DIR\"")
        ;;
    *.gz)
        echo "Extracting $FILENAME (gzip)..."
        OUTPUT=$(run_command "gzip -dk \"$FILE\" && mv \"${FILE%.gz}\" \"$EXTRACT_DIR/\"")
        ;;
    *.bz2)
        echo "Extracting $FILENAME (bzip2)..."
        OUTPUT=$(run_command "bzip2 -dk \"$FILE\" && mv \"${FILE%.bz2}\" \"$EXTRACT_DIR/\"")
        ;;
    *.xz)
        echo "Extracting $FILENAME (xz)..."
        OUTPUT=$(run_command "xz -dk \"$FILE\" && mv \"${FILE%.xz}\" \"$EXTRACT_DIR/\"")
        ;;
    *.zip)
        echo "Extracting $FILENAME (zip)..."
        OUTPUT=$(run_command "unzip -q \"$FILE\" -d \"$EXTRACT_DIR\"")
        ;;
    *.tar)
        echo "Extracting $FILENAME (tar)..."
        OUTPUT=$(run_command "tar -xf \"$FILE\" -C \"$EXTRACT_DIR\"")
        ;;
    *)
        echo "Error: Unsupported file format for '$FILENAME'"
        exit 1
        ;;
esac

# Check if extraction succeeded
if [ $? -eq 0 ]; then
    echo "Success! Extracted to: $EXTRACT_DIR"
    echo "$OUTPUT" | while read -r line; do
        echo "  → $line"
    done
else
    echo "Extraction failed! Error:"
    echo "$OUTPUT"
    exit 1
fi

# Keep original archive in Downloads
echo "Original archive kept: $FILE"