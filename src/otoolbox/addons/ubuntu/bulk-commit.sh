#!/bin/bash
# Constants
WORKDIR="$(pwd)"
PROCESS_DATE=$(date +%Y-%m-%d)
LOG_FILE="$WORKDIR/commit-log-$PROCESS_DATE.log"

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
        git add .
        git commit -m "[CP] Commit all changes due to bulky process (such as precommit) on $PROCESS_DATE" >> "$LOG_FILE" 2>&1
    fi
done