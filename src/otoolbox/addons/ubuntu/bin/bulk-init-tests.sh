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
WORKDIR=$(pwd -P)  # Use pwd with -P flag for canonicalization
PRECOMMIT_DATE=$(date +"%Y-%m-%d")  # Use format string to avoid locale issues
LOG_FILE="${WORKDIR}/.logs/init-test-log-${PRECOMPUT_DATE}.log"  # Use double quotes and template strings
mkdir -p "${WORKDIR}/.logs"

# load variables
source .env

# ... rest of the code remains the same ...

# copy changes to the repo
echo "Current directory is: $CURRENT_DIR"
cd "$WORKDIR"

#For each folder in moonsun (it must be part of a shielded project)
for dir in "$WORKDIR/odoonix"/*/; do
    if [ -d "$dir" ]; then
        project=$(basename "$dir")
        echo ""
        echo "===================================================================="
        echo "Repository: $project"
        echo "Path: $dir"
        echo "===================================================================="
        cd "$dir"
        

        for addon_dir in "$WORKDIR/odoonix/$project"/*; do
            if [ -d "$addon_dir" ]; then
                if [ -f "$addon_dir/__manifest__.py" ]; then
                    addon_name=$(basename "$addon_dir")
                    echo   "Processing addon: $addon_name"

                    ####################################################################
                    # Test directory
                    if [ -d "$addon_dir/tests/__init__.py" ]; then
                        rm -fR "$addon_dir/tests/__init__.py"
                    fi

                    if [ ! -d "$addon_dir/tests" ]; then
                        mkdir -p "$addon_dir/tests"
                    fi
                    
                    touch "$addon_dir/tests/__init__.py"
                fi
            fi
        done

    fi
done


