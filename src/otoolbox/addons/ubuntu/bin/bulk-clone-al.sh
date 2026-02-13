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
repos=(
    "odoonix/account" \
    "odoonix/brand" \
    "odoonix/cnp" \
    "odoonix/connector" \
    "odoonix/docker-postgres" \
    "odoonix/education" \
    "odoonix/exchange" \
    "odoonix/exchange-mp" \
    "odoonix/gmt" \
    "odoonix/gpu" \
    "odoonix/gym" \
    "odoonix/hr" \
    "odoonix/iot" \
    "odoonix/municipality" \
    "odoonix/nesa" \
    "odoonix/odoo-book-development" \
    "odoonix/online" \
    "odoonix/partner-contact" \
    "odoonix/payment" \
    "odoonix/pep" \
    "odoonix/pos" \
    "odoonix/product" \
    "odoonix/purchase" \
    "odoonix/sale" \
    "odoonix/server-tools" \
    "odoonix/server-ux" \
    "odoonix/sms" \
    "odoonix/social" \
    "odoonix/stock" \
    "odoonix/tb-gateway" \
    "odoonix/website" \
)

for project in "${repos[@]}"; do
    echo ">>> Processing: $project"
    otoolbox --no-silent repo add $project
    echo "---------------------------"
done

