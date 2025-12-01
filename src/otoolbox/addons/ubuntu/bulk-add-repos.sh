#!/bin/bash

# Supported repositoires
paths=(
    # OCA
    "oca/pos"

    # Odoonix
)

# Add them all
for path in "${paths[@]}"; do
    echo "Adding repo: $path"
    otoolbox --silent --no-pre-check --no-post-check repo add "$path"
done
