#!/bin/bash
# This script is used to apply changes to the Odoo modules based on recent edits.

# Login as worker (woker is a user with permissions to commit changes to moonsun)
# su - worker 

# Constants
WORKDIR="$(pwd)"
SYNC_DATE=$(date +%Y-%m-%d)
LOG_FILE="$WORKDIR/sync-log-$SYNC_DATE.log"

# copy changes to the moonsunsoft repo
echo "Current directory is: $CURRENT_DIR"
echo "Copying changes to moonsunsoft repository..."
cd "$WORKDIR"
otoolbox repo sync-shielded > "$LOG_FILE" 2>&1

#For each folder in moonsun (it must be part of a shielded project)
for dir in "$WORKDIR/moonsunsoft"/*/; do
    if [ -d "$dir" ]; then
        project=$(basename "$dir")
        echo "Processing project: $project"
        echo "push changes to moonsunsoft/$project" >> "$LOG_FILE" 2>&1
        cd "$WORKDIR/moonsunsoft/$project"
        # commit and push changes
        git pull >> "$LOG_FILE" 2>&1
        git add . >> "$LOG_FILE" 2>&1
        git commit -m "[SYNC] Update to the latest release on $SYNC_DATE" >> "$LOG_FILE" 2>&1
        git push >> "$LOG_FILE" 2>&1
    fi
done