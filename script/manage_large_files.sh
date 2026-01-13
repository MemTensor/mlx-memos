#!/bin/bash

# Define the size limit (1.9GB to be safe for GitHub 2GB limit)
CHUNK_SIZE="1900m"

function split_files() {
    echo "Searching for files larger than $CHUNK_SIZE..."
    find models -type f -size +1900M | while read -r file; do
        if [[ "$file" == *.part_* ]]; then
            continue
        fi
        
        echo "Splitting $file..."
        split -b $CHUNK_SIZE "$file" "$file.part_"
        
        if [ $? -eq 0 ]; then
            echo "Successfully split $file"
            # Verify the split
            # echo "Verifying split..."
            # cat "$file.part_"* > "$file.tmp"
            # diff "$file" "$file.tmp"
            # rm "$file.tmp"
            
            # Remove the original file to avoid uploading it
            rm "$file"
            echo "Removed original file $file (it can be restored by merging parts)"
        else
            echo "Failed to split $file"
        fi
    done
}

function merge_files() {
    echo "Searching for split files..."
    find models -name "*.part_aa" | while read -r part_file; do
        base_file="${part_file%.part_aa}"
        
        if [ -f "$base_file" ]; then
            echo "Target file $base_file already exists. Skipping merge."
            continue
        fi
        
        echo "Merging into $base_file..."
        cat "${base_file}.part_"* > "$base_file"
        
        if [ $? -eq 0 ]; then
            echo "Successfully merged $base_file"
        else
            echo "Failed to merge $base_file"
        fi
    done
}

case "$1" in
    "split")
        split_files
        ;;
    "merge")
        merge_files
        ;;
    *)
        echo "Usage: $0 {split|merge}"
        exit 1
        ;;
esac
