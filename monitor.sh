#!/bin/bash

WATCH_DIR="Downloads/"
DECOMPRESS_SCRIPT="./autodescomp.sh"
SUPPORTED_EXTS=("gz" "bz2" "xz" "zip" "tar" "tgz" "tbz2" "txz" "tar.gz" "tar.bz2" "tar.xz")

find "$WATCH_DIR" -type f -name '*.*' -print0 | while IFS= read -r -d '' FILE; do
    for ext in "${SUPPORTED_EXTS[@]}"; do
        if [[ "$FILE" == *".$ext" ]]; then
            echo "Found archive: $(basename "$FILE")"
            $DECOMPRESS_SCRIPT "$FILE" && rm -f "$FILE"  # Optional: Delete after extraction
            break
        fi
    done
done