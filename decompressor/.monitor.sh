#!/bin/bash
WATCH_DIR="Downloads/"
DECOMPRESS_SCRIPT="./autodescomp.sh"

find "$WATCH_DIR" -type f -name '*.*' -print0 | while read -r FILE
do
    if [[ "$FILE" =~ \.(gz|bz2|xz|zip|tar|tgz|tbz2|txz)$ ]]; then
        echo "Detected new archive: $FILE"
        sleep 1  # Ensure file is fully downloaded
        "$DECOMPRESS_SCRIPT" "$WATCH_DIR/$FILE"
    fi
done