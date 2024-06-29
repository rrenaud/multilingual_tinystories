#!/bin/bash

# Define directories
SOURCE_DIR="/home/rrenaud/multilingual_tinystories/spanish_stories"
TEMP_DIR="/home/rrenaud/multilingual_tinystories/temp_directory"
TARGET_DIR="/home/rrenaud/multilingual_tinystories/tarred_stories"

# Ensure temp and target directories exist
mkdir -p "$TEMP_DIR"
mkdir -p "$TARGET_DIR"

# Move all files from source to temp directory using find and xargs
find "$SOURCE_DIR" -type f -print0 | xargs -0 -I {} mv {} "$TEMP_DIR/"

# Count the number of files in the temp directory
FILE_COUNT=$(ls -1 "$TEMP_DIR" | wc -l)

# Create a tarball of all files in the temp directory
TARBALL_NAME="stories_${FILE_COUNT}_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$TARGET_DIR/$TARBALL_NAME" -C "$TEMP_DIR" .

# Check if the tarball was created successfully
if [ -f "$TARGET_DIR/$TARBALL_NAME" ]; then
    rm -rf "$TEMP_DIR"
else
    echo "Error: Failed to create tarball."
fi
