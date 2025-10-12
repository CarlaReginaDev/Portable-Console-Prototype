#!/bin/bash

# Configuration
DOWNLOAD_DIR="Downloads"
EXTRACT_DIR="Downloads/games"
DECOMPRESSOR_SCRIPT="./decompressor.sh"
OUTPUT_FILE="games_list.txt"
LOG_FILE="decompression.log"
PYTHON_SCRIPT="jsonconverter.py"
PYTHON_SCRIPT_ARGS="games_list.txt $EXTRACT_DIR -o ~/playground/IFRN/Portable-Console-Prototype/GUI/games.json"

# Common ROM file extensions, used for USB and loose file checks
ROM_EXTENSIONS=(
    "smc" "gb" "gbc" "gba" "gen" "md" "smd" "iso" "cue" "bin" "ps1" "sfc"
)

# Function to log messages, now writing to stderr and the log file
log_message() {
    local timestamped_message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$timestamped_message" >&2
    echo "$timestamped_message" >> "$LOG_FILE"
}

# --- SCRIPT DEPENDENCY CHECKS (UNCHANGED) ---
check_decompressor_script() {
    if [ ! -f "$DECOMPRESSOR_SCRIPT" ]; then
        log_message "ERROR: Decompressor script not found at $DECOMPRESSOR_SCRIPT"
        exit 1
    fi
    if [ ! -x "$DECOMPRESSOR_SCRIPT" ]; then
        chmod +x "$DECOMPRESSOR_SCRIPT"
    fi
}
check_python_script() {
    if ! command -v python3 &> /dev/null; then log_message "WARNING: python3 not found. JSON conversion will be skipped."; return 1; fi
    if [ ! -f "$PYTHON_SCRIPT" ]; then log_message "WARNING: Python script not found at $PYTHON_SCRIPT. JSON conversion will be skipped."; return 1; fi
    log_message "Python3 and JSON converter script are available"
    return 0
}
run_json_converter() {
    local output_file="$1"
    if [ ! -f "$output_file" ]; then log_message "WARNING: Games list file not found: $output_file. Skipping JSON conversion."; return 1; fi
    local rom_count=$(wc -l < "$output_file" 2>/dev/null || echo 0)
    if [ "$rom_count" -eq 0 ]; then log_message "WARNING: No ROMs found in $output_file. Skipping JSON conversion."; return 1; fi
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

# --- DIRECTORY AND HELPER FUNCTIONS (UNCHANGED) ---
create_extract_dir() {
    if [ ! -d "$EXTRACT_DIR" ]; then mkdir -p "$EXTRACT_DIR"; log_message "Created extraction directory: $EXTRACT_DIR"; fi
}
find_compressed_files() {
    find "$DOWNLOAD_DIR" -maxdepth 1 -type f \( -name "*.zip" -o -name "*.rar" -o -name "*.7z" -o -name "*.tar" -o -name "*.tar.gz" -o -name "*.tgz" -o -name "*.tar.bz2" -o -name "*.tbz" -o -name "*.tar.xz" -o -name "*.txz" -o -name "*.gz" -o -name "*.bz2" -o -name "*.xz" \) -print0
}
count_roms() {
    if [[ -f "$OUTPUT_FILE" ]]; then wc -l < "$OUTPUT_FILE" 2>/dev/null | tr -d ' '; else echo "0"; fi
}
cleanup_temp_dirs() {
    local temp_dirs=$(find "$EXTRACT_DIR" -name ".temp_*" -type d 2>/dev/null)
    if [[ -n "$temp_dirs" ]]; then
        log_message "Cleaning up temporary directories..."
        echo "$temp_dirs" | while read -r dir; do if [[ -d "$dir" ]]; then rm -rf "$dir"; log_message "Removed temporary directory: $dir"; fi; done
    fi
}

# --- NEW FUNCTION: Check for and copy files from USB drives ---
check_usb_drives() {
    log_message "=== Checking for USB drives ==="
    if ! command -v lsblk &> /dev/null; then
        log_message "WARNING: 'lsblk' command not found. Skipping USB drive check."
        return
    fi
    
    # Find mounted USB drives
    lsblk -o MOUNTPOINT,TRAN | grep -i "usb" | awk '{print $1}' | while read -r mount_point; do
        if [ -d "$mount_point" ]; then
            log_message "Found USB drive at: $mount_point"
            
            # Check if we have processed this drive before
            if [ -f "$mount_point/.processed_by_monitor" ]; then
                log_message "USB drive already processed. Skipping."
                continue
            fi
            
            log_message "Searching for new files on USB drive..."
            # Use rsync to copy new compressed files and ROMs
            # -a: archive mode, -v: verbose, --ignore-existing, --progress
            rsync -av --ignore-existing --progress "$mount_point/" "$DOWNLOAD_DIR/" \
                --include='*.zip' --include='*.rar' --include='*.7z' \
                $(for ext in "${ROM_EXTENSIONS[@]}"; do echo "--include=**/*.$ext"; done) \
                --exclude='*'
            
            log_message "Finished copying files from $mount_point"
            # Mark the drive as processed
            touch "$mount_point/.processed_by_monitor"
            log_message "Marked USB drive as processed."
        fi
    done
}

# --- NEW FUNCTION: Process loose ROMs in the Downloads folder ---
process_loose_roms() {
    log_message "=== Checking for loose ROM files in $DOWNLOAD_DIR ==="
    local new_rom_found=0
    
    # Build find command arguments for all ROM extensions
    local find_args=()
    for ext in "${ROM_EXTENSIONS[@]}"; do
        find_args+=(-o -name "*.$ext")
    done
    # Remove the first "-o"
    unset find_args[0]
    
    # Find all loose ROMs in the download directory
    find "$DOWNLOAD_DIR" -maxdepth 1 -type f \( "${find_args[@]}" \) -print0 | while IFS= read -r -d '' rom_file; do
        local filename=$(basename "$rom_file")
        
        # Check if the ROM is already in our list
        if grep -q -x "$filename" "$OUTPUT_FILE"; then
            log_message "Duplicate loose ROM found, deleting: $filename"
            rm "$rom_file"
        else
            log_message "New loose ROM found: $filename. Moving to games folder."
            # Move the new ROM to the games directory
            if mv "$rom_file" "$EXTRACT_DIR/"; then
                # Add the new ROM to the list
                echo "$filename" >> "$OUTPUT_FILE"
                log_message "✓ Added $filename to the list."
                new_rom_found=1
            else
                log_message "✗ Failed to move $filename."
            fi
        fi
    done
    
    if [ "$new_rom_found" -eq 0 ]; then
        log_message "No new loose ROMs found."
    fi
}

# --- MAIN PROCESSING LOGIC (UNCHANGED CORE, MODIFIED FLOW) ---
process_compressed_files() {
    local file_count=0
    cleanup_temp_dirs
    log_message "Searching for compressed files in $DOWNLOAD_DIR..."
    file_count=$(find_custom_compressed_files | tr '\0' '\n' | wc -l)
    
    if [ $file_count -eq 0 ]; then
        log_message "No compressed files found to process."
        return 0
    fi
    
    log_message "Found $file_count compressed file(s) to process."
    
    find_compressed_files | while IFS= read -r -d '' file; do
        local filename=$(basename "$file")
        log_message "=== Processing: $filename ==="
        if "$DECOMPRESSOR_SCRIPT" "$file" "$EXTRACT_DIR" "$OUTPUT_FILE"; then
            log_message "✓ Successfully processed: $filename"
        else
            log_message "✗ Failed to process: $filename"
        fi
        log_message "=== Completed: $filename ==="
    done
    
    cleanup_temp_dirs
    local rom_count=$(count_roms)
    log_message "Compressed file processing complete. Total ROMs in list: $rom_count."
    return 0
}

# --- MODIFIED Main execution flow ---
main() {
    log_message "======= SCRIPT START ======="
    check_decompressor_script
    create_extract_dir
    # Ensure the output file exists to prevent errors on the first run
    touch "$OUTPUT_FILE"

    # 1. Check for files on USB drives
    check_usb_drives
    
    # 2. Process any loose ROMs already in Downloads
    process_loose_roms

    # 3. Process compressed files
    process_compressed_files
    
    # 4. Convert to JSON if possible
    check_python_script
    local python_available=$?
    local rom_count=$(count_roms)
    
    if [ $python_available -eq 0 ] && [ "$rom_count" -gt 0 ]; then
        log_message "=== Starting JSON conversion ==="
        run_json_converter "$OUTPUT_FILE"
    elif [ "$rom_count" -eq 0 ]; then
        log_message "No ROMs in list, skipping JSON conversion."
    else
        log_message "Python not available, skipping JSON conversion."
    fi
    
    log_message "======= SCRIPT FINISHED ======="
}

# Run main function
main "$@"