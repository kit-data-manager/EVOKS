#!/bin/bash


# Replaces the skosmos:baseHref value in the specified file with the provided basehref value.
# Args:
#     file_path (str): The path to the file to be updated.
#     basehref (str): The new baseHref value to be set in the file.
# Raises:
#     ValueError: If the file content or the updated content is empty.
#     Exception: If any error occurs during the file operations.

replace() {
    local file_path="$1"
    local basehref="$2"

    # Get the current timestamp for the backup file
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_path="${file_path}.${timestamp}.backup"

    # Check if the file exists
    if [[ ! -f "$file_path" ]]; then
        echo "File '$file_path' does not exist. Aborting."
        exit 1
    fi

    # Read the content of the file
    local content
    content=$(cat "$file_path")

    # Validate that the file is not empty
    if [[ -z "${content// /}" ]]; then
        echo "config.ttl seems to be empty. Aborting operation to avoid overwriting."
        exit 1
    fi

    # Replace the skosmos:baseHref value using | as the delimiter
    local updated_content
    updated_content=$(echo "$content" | sed -E 's|skosmos:baseHref[[:space:]]*[^;]*;|skosmos:baseHref "'"$basehref"'" ;|')
    # Validate the updated content is not empty
    if [[ -z "${updated_content// /}" ]]; then
        echo "Updated content of config.ttl is empty. Aborting operation to avoid overwriting."
        exit 1
    fi

    # Create a backup of the original file
    echo "$content" > "$backup_path"

    # Write the updated content to a temporary file first
    local temp_file_path="${file_path}.temp"
    echo "$updated_content" > "$temp_file_path"

    # Replace the original file with the temporary file's content
    if ! mv "$temp_file_path" "$file_path"; then
        echo "File is busy, attempting to copy instead."
        if cp "$temp_file_path" "$file_path"; then
            rm "$temp_file_path"
            echo "File '$file_path' updated successfully using copy."
        else
            echo "Failed to update the file using copy. Aborting."
            exit 1
        fi
    else
        echo "File '$file_path' updated successfully."
    fi

}

# Main script logic
if [[ "$#" -ne 2 ]]; then
    echo "Usage: $0 <file_path> <basehref>"
    exit 1
fi

file_path="$1"
basehref="$2"

replace "$file_path" "$basehref"
