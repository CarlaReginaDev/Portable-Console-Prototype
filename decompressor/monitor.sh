#!/bin/bash

# Configuration
DOWNLOAD_DIR="Downloads"
EXTRACT_DIR="Downloads/games"
DECOMPRESSOR_SCRIPT="./decompressor.sh"
OUTPUT_FILE="games_list.txt"
LOG_FILE="decompression.log"
PYTHON_SCRIPT="jsonconverter.py"
PYTHON_SCRIPT_ARGS="games_list.txt $EXTRACT_DIR -o /home/kleber/playground/IFRN/Portable-Console-Prototype/GUI/games.json"

# Function to log messages, now writing to stderr and the log file
log_message() {
    local timestamped_message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$timestamped_message" >&2
    echo "$timestamped_message" >> "$LOG_FILE"
}

# Function to check if decompressor script exists
check_decompressor_script() {
    if [ ! -f "$DECOMPRESSOR_SCRIPT" ]; then
        log_message "ERROR: Decompressor script not found at $DECOMPRESSOR_SCRIPT"
        exit 1
    fi
    if [ ! -x "$DECOMPRESSOR_SCRIPT" ]; then
        chmod +x "$DECOMPRESSOR_SCRIPT"
    fi
}

# Function to check if Python script exists and Python is available
check_python_script() {
    if ! command -v python3 &> /dev/null; then
        log_message "WARNING: python3 not found. JSON conversion will be skipped."
        return 1
    fi
    
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        log_message "WARNING: Python script not found at $PYTHON_SCRIPT. JSON conversion will be skipped."
        return 1
    fi
    
    log_message "Python3 and JSON converter script are available"
    return 0
}

# Function to run Python JSON converter
run_json_converter() {
    local output_file="$1"
    
    if [ ! -f "$output_file" ]; then
        log_message "WARNING: Games list file not found: $output_file. Skipping JSON conversion."
        return 1
    fi
    
    local rom_count=$(wc -l < "$output_file" 2>/dev/null || echo 0)
    
    if [ "$rom_count" -eq 0 ]; then
        log_message "WARNING: No ROMs found in $output_file. Skipping JSON conversion."
        return 1
    fi
    
    log_message "Running JSON converter: python3 $PYTHON_SCRIPT $PYTHON_SCRIPT_ARGS"
    
    if python3 "$PYTHON_SCRIPT" games_list.txt "$EXTRACT_DIR" -o games.json; then
        log_message "✓ JSON conversion successful. Output: $EXTRACT_DIR/games.json"
        log_message "✓ Converted $rom_count ROMs to JSON format"
        return 0
    else
        log_message "✗ JSON conversion failed with exit code $?"
        return 1
    fi
}

# Function to create extract directory
create_extract_dir() {
    if [ ! -d "$EXTRACT_DIR" ]; then
        mkdir -p "$EXTRACT_DIR"
        log_message "Created extraction directory: $EXTRACT_DIR"
    fi
}

# Function to find compressed files (handles spaces)
find_compressed_files() {
    find "$DOWNLOAD_DIR" -maxdepth 1 -type f \( \
        -name "*.zip" -o \
        -name "*.rar" -o \
        -name "*.7z" -o \
        -name "*.tar" -o \
        -name "*.tar.gz" -o \
        -name "*.tgz" -o \
        -name "*.tar.bz2" -o \
        -name "*.tbz" -o \
        -name "*.tar.xz" -o \
        -name "*.txz" -o \
        -name "*.gz" -o \
        -name "*.bz2" -o \
        -name "*.xz" \
    \) -print0
}

# Function to count ROMs in output file
count_roms() {
    if [[ -f "$OUTPUT_FILE" ]]; then
        wc -l < "$OUTPUT_FILE" 2>/dev/null | tr -d ' '
    else
        echo "0"
    fi
}

# Function to clean up temporary directories
cleanup_temp_dirs() {
    local temp_dirs=$(find "$EXTRACT_DIR" -name ".temp_*" -type d 2>/dev/null)
    if [[ -n "$temp_dirs" ]]; then
        log_message "Cleaning up temporary directories..."
        echo "$temp_dirs" | while read -r dir; do
            if [[ -d "$dir" ]]; then
                rm -rf "$dir"
                log_message "Removed temporary directory: $dir"
            fi
        done
    fi
}

# Function to process compressed files (handles spaces)
process_compressed_files() {
    local file_count=0
    
    # Clean up any existing temporary directories first
    cleanup_temp_dirs
    
    # Count files first
    log_message "Searching for compressed files in $DOWNLOAD_DIR..."
    file_count=$(find_compressed_files | while IFS= read -r -d '' file; do 
        log_message "Found: $(basename "$file")"
        echo "1"
    done | wc -l)
    
    if [ $file_count -eq 0 ]; then
        log_message "No compressed files found in $DOWNLOAD_DIR"
        return 0
    fi
    
    log_message "Found $file_count compressed file(s)"
    
    # Process each file
    find_compressed_files | while IFS= read -r -d '' file; do
        local filename=$(basename "$file")
        log_message "=== Processing: $filename ==="
        
        # Call decompressor script
        if "$DECOMPRESSOR_SCRIPT" "$file" "$EXTRACT_DIR" "$OUTPUT_FILE"; then
            log_message "✓ Successfully processed: $filename"
        else
            log_message "✗ Failed to process: $filename"
        fi
        
        log_message "=== Completed: $filename ==="
    done
    
    # Clean up any remaining temporary directories
    cleanup_temp_dirs
    
    # Count how many ROMs were actually found
    local rom_count=$(count_roms)
    
    log_message "All files processed. Found $rom_count ROM(s). List saved to: $OUTPUT_FILE"
    log_message "Extracted files are in: $EXTRACT_DIR"
    
    return 0
}

# Main execution
main() {
    log_message "=== Starting compressed file check ==="
    check_decompressor_script
    create_extract_dir
    
    # Check if Python script is available
    check_python_script
    local python_available=$?
    
    # Initialize output file (clear it only once at the beginning)
    > "$OUTPUT_FILE"
    log_message "Initialized output file: $OUTPUT_FILE"
    
    # Process files
    process_compressed_files
    
    # Count ROMs after processing
    local rom_count=$(count_roms)
    
    # Run JSON converter if Python is available and ROMs were found
    if [ $python_available -eq 0 ] && [ "$rom_count" -gt 0 ]; then
        log_message "=== Starting JSON conversion ==="
        run_json_converter "$OUTPUT_FILE"
    elif [ "$rom_count" -eq 0 ]; then
        log_message "No ROMs found, skipping JSON conversion"
    else
        log_message "Python script not available, skipping JSON conversion"
    fi
    
    log_message "=== Script finished ==="
}

# Run main function
main "$@"