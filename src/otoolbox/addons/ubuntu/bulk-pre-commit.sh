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
LOG_FILE="${WORKDIR}/precommit-log-${PRECOMPUT_DATE}.log"  # Use double quotes and template strings

# load variables
source .env

# ... rest of the code remains the same ...

# copy changes to the repo
echo "Current directory is: $CURRENT_DIR"
cd "$WORKDIR"

# install or update maintainer tools
# pipx \
#     install \
#     --force \
#     oca-maintainers-tools@git+https://github.com/OCA/maintainer-tools.git


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
                    # Documents
                    # commit and push changes
                    # https://github.com/OCA/oca-addons-repo-template
                    doc_files=( \
                        "/readme/CONFIGURE" \
                        "/readme/CONTEXT" \
                        "/readme/CONTRIBUTORS" \
                        "/readme/CREDITS" \
                        "/readme/DESCRIPTION" \
                        "/readme/DEVELOP" \
                        "/readme/HISTORY" \
                        "/readme/INSTALL" \
                        "/readme/ROADMAP" \
                        "/readme/USAGE" \
                        "/README" \
                        "/doc/index"
                    )
                    doc_dirs=(\
                        "/readme" \
                        "/doc"
                    )
                    for doc_dir in "${doc_dirs[@]}"; do
                        mkdir -p "$addon_dir/$doc_dir"
                    done

                    for doc_file in "${doc_files[@]}";do

                        if [ -f "${addon_dir}/${doc_file}.md" ]; then
                            mv -f \
                                "${addon_dir}/${doc_file}.md" \
                                "${addon_dir}/${doc_file}.rst"
                        fi
                        touch "${addon_dir}/${doc_file}.rst"
                    done
                fi
            fi
        done

        #
        #  Precommit
        #
        pre-commit run -a > "$LOG_FILE" 2>&1

        #
        # Generage customer readme
        #
        if [ -f "$WORKDIR/gen_addon_readme.rst.jinja" ]; then
            cp -f "$WORKDIR/gen_addon_readme.rst.jinja" "$dir/gen_addon_readme.rst.jinja"
        fi
        if [ -f "$dir/gen_addon_readme.rst.jinja" ]; then
            oca-gen-addon-readme \
                --addons-dir="$dir" \
                --branch=${ODOO_VERSION} \
                --org-name=${SHIELDED_ORGANIZATION} \
                --repo-name=$project \
                --if-source-changed \
                --keep-source-digest \
                --template-filename=./gen_addon_readme.rst.jinja
        fi
    fi
done


