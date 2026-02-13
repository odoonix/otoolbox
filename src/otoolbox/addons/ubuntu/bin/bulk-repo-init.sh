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
PRECOMMIT_DATE=$(date +%Y-%m-%d)
LOG_FILE="$WORKDIR/precommit-log-$PRECOMMIT_DATE.log"


# load variables
source .env

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
        # https://github.com/OCA/oca-addons-repo-template
        # if the project is not init
        cp -f \
            "$WORKDIR/gen_addon_readme.rst.jinja" \
            "$WORKDIR/odoonix/$project/gen_addon_readme.rst.jinja"
        if [ ! -f ".copier-answers.yml" ]; then
            echo "Project $project is not initialized, initializing..."
            cp \
                "$WORKDIR/copier-answers.yml" \
                "$WORKDIR/odoonix/$project/.copier-answers.yml"
            copier copy \
                --UNSAFE \
                --overwrite \
                --answers-file ".copier-answers.yml" \
                https://github.com/OCA/oca-addons-repo-template.git .
        else
            # if the project is init
            echo "Project $project is already initialized."
            copier update \
                --UNSAFE \
                --skip-answered \
                --answers-file ".copier-answers.yml" 
        fi
    fi
done