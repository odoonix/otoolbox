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
        # commit and push changes
        git pull
        git push
    fi
done
