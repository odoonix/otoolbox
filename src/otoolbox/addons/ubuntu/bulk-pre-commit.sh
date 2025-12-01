#!/bin/bash
# Constants
WORKDIR="$(pwd)"
PRECOMMIT_DATE=$(date +%Y-%m-%d)
LOG_FILE="$WORKDIR/precommit-log-$PRECOMMIT_DATE.log"

# copy changes to the moonsunsoft repo
echo "Current directory is: $CURRENT_DIR"
cd "$WORKDIR"

#For each folder in moonsun (it must be part of a shielded project)
for dir in "$WORKDIR/odoonix"/*/; do
    if [ -d "$dir" ]; then
        project=$(basename "$dir")
        echo "Processing project: $project"
        cd "$WORKDIR/odoonix/$project"
        pwd
        # commit and push changes
        pre-commit run -a
    fi
done
