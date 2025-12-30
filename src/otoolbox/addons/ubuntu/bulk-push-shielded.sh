#!/bin/bash
#############################################################################
#                                                                           #
# This file is part of the "ubuntu" module of the otoolbox project.         #
#                                                                           #
# This script is open-source and intended for automation purposes.          #
# It is distributed in the hope that it will be useful, but WITHOUT         #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY        #
# or FITNESS FOR A PARTICULAR PURPOSE.                                      #
#                                                                           #
# Use of this script is entirely at your own risk.                          #
#                                                                           #
# Copyright (c) The otoolbox contributors.                                  #
#############################################################################

# NOTE: This script is used to apply changes to the Odoo modules based on
# recent edits.
# Login as worker (woker is a user with permissions to commit changes to moonsun)
# su - worker 

# Constants
WORKDIR="$(pwd)"
SYNC_DATE=$(date +%Y-%m-%d)
LOG_FILE="$WORKDIR/sync-log-$SYNC_DATE.log"



# Pull all
for dir in "$WORKDIR/moonsunsoft"/*; do
    if [ -d "$dir" ]; then
        project=$(basename "$dir")
        echo "Pull project: $project"
        cd "$dir"
        git config --global --add safe.directory "$dir"
        # commit and push changes
        git pull >> "$LOG_FILE" 2>&1
    fi
done


# copy changes to the moonsunsoft repo
echo "Current directory is: $CURRENT_DIR"
echo "Copying changes to moonsunsoft repository..."
cd "$WORKDIR"
otoolbox repo sync-shielded > "$LOG_FILE" 2>&1

# Push all
for dir in "$WORKDIR/moonsunsoft"/*; do
    if [ -d "$dir" ]; then
        project=$(basename "$dir")
        echo "Processing project: $project"
        echo "push changes to moonsunsoft/$project" >> "$LOG_FILE" 2>&1
        cd "$dir"
        git config --global --add safe.directory "$dir"
        # commit and push changes
        git add . >> "$LOG_FILE" 2>&1
        git commit -m "[SYNC] Update to the latest release on $SYNC_DATE" >> "$LOG_FILE" 2>&1
        git push >> "$LOG_FILE" 2>&1
    fi
done