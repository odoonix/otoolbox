
REPOSITORIES_PATH = "repositoires.json"
RESOURCE_REPOSITORIES_PATH = "repositories.json"
GIT_ADDRESS_HTTPS = "https://github.com/{path}.git"
GIT_ADDRESS_SSH = "git@github.com:{path}.git"

GIT_ERROR_TABLE = {
    2: {
        'level': 'fatal',
        'message': "Resource {path}, doese not exist or is not a git repository."
    },
    128: {
        'level': 'fatal',
        'message': "Destination path '{path}' already exists and is not an empty directory."
    }
    # TODO: Add more error message and find related error code
    # Example of error message that is not coverd
    # warning: Could not find remote branch 19.0 to clone.
    # fatal: Remote branch 19.0 not found in upstream origin
}

GIT_COMMAND = "git"