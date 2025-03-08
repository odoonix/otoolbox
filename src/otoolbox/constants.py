
ERROR_CODE_PRE_VERIFICATION = 19841
ERROR_CODE_POST_VERIFICATION = 19842


RESOURCE_PREFIX_VIRTUAL = 'virtual://'
RESOURCE_PREFIX_APPLICATION = 'app://'

#
# Resource priorities
#
# The priority of the resource. The higher the number, the higher the priority.
# The priority is used to determine the order in which the resources are processed.
# Here is list of priorities:
# - RESOURCE_PRIORITY_DEFAULT: default priority
# - RESOURCE_PRIORITY_ROOT: root resources (should be processed first)
# - RESOURCE_PRIORITY_EXTEND: resources that extend the root or default resources
#
RESOURCE_PRIORITY_DEFAULT = 100
RESOURCE_PRIORITY_ROOT = 200
RESOURCE_PRIORITY_EXTEND = 50


#
# Common resource paths
# 
RESOURCE_ROOT = "."
RESOURCE_ENV_FILE = ".env"



RESOURCE_TAGS_ENV = "env"
RESOURCE_TAGS_GIT = "git"
RESOURCE_TAGS_AUTO_UPDATE = "auto_update"
RESOURCE_TAGS_AUTO_VERIFY = "auto_verify"


