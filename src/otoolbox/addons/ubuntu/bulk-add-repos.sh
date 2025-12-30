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



bulk-add-repos.sh 
bulk-clone-al.sh 
bulk-commit.sh 
bulk-init-tests.sh 
bulk-pre-commit.sh 
bulk-pull.sh 
bulk-push-shielded.sh 
bulk-push.sh 
bulk-repo-init.sh