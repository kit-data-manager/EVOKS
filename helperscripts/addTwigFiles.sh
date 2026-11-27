#!/bin/bash


# Add empty twig files to some directories to prevent SKOSMOS to display placeholders.
# Args:
#     -
# Raises:
#     Exception: If any error occurs during the file operations.

TWIG_DIRECTORIES=(
    "/var/www/html/custom-templates/landing-end"
    "/var/www/html/custom-templates/landing-start"
)

for dir in "${TWIG_DIRECTORIES[@]}"; do
    if ! ls "$dir"/*.twig >/dev/null 2>&1; then
        echo "No twig file available in $dir -> create empty.twig"
        touch "$dir/empty.twig"
    fi
done
